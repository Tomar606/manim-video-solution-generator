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
# The default view is the pipeline itself, numbered, because most people opening
# this have never touched the CLI and do not know our stage names. Each step is
# described by what it produces in plain words, and stays disabled with a stated
# reason until the stages it depends on have run — so the order cannot be got
# wrong by clicking. The non-linear editor is one tab away for anyone who wants
# to edit individual beats: a beat is a clip, and each stage is a track over
# those clips.
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
body{font:13px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;
     background:var(--bg);color:var(--txt);height:100vh;overflow:hidden}
button{font:inherit;cursor:pointer;border:0;border-radius:6px;
       background:var(--panel2);color:var(--txt);padding:7px 12px}
button:hover:not(:disabled){background:#2a3242}
button:disabled{opacity:.35;cursor:not-allowed}
button.primary{background:var(--accent);color:#fff;font-weight:600}
button.primary:hover:not(:disabled){background:#6d9bf5}
button.danger{background:var(--bad);color:#fff}
button.big{padding:11px 20px;font-size:14px}
input,textarea,select{font:inherit;background:var(--track);color:var(--txt);
  border:1px solid var(--line);border-radius:6px;padding:8px 10px;width:100%}
textarea{resize:vertical;font-family:inherit}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px}
.dim{color:var(--dim)}
.row{display:flex;gap:8px;align-items:center}
.hide{display:none!important}

#app{display:grid;height:100vh;
     grid-template-rows:52px minmax(0,1fr) auto;
     grid-template-columns:250px minmax(0,1fr);
     grid-template-areas:"top top" "bins main" "drawer drawer"}

/* ---------- toolbar ---------- */
#top{grid-area:top;display:flex;align-items:center;gap:14px;padding:0 16px;
     background:var(--panel);border-bottom:1px solid var(--line)}
#top h1{font-size:15px;font-weight:600;white-space:nowrap}
#top .sep{width:1px;height:24px;background:var(--line)}
#tabs{display:flex;gap:4px}
#tabs button{font-size:12.5px;padding:6px 14px;background:transparent;color:var(--dim)}
#tabs button.on{background:var(--panel2);color:var(--txt);font-weight:600}

/* ---------- left bin ---------- */
#bins{grid-area:bins;background:var(--panel);border-right:1px solid var(--line);
      overflow:auto;padding:12px}
.binhead{font-size:11px;text-transform:uppercase;letter-spacing:.07em;
         color:var(--dim);margin:16px 0 8px}
.binhead:first-child{margin-top:0}
.item{padding:8px 10px;border-radius:6px;cursor:pointer;font-size:12.5px}
.item:hover{background:var(--panel2)}
.item.sel{background:var(--panel2);box-shadow:inset 2px 0 0 var(--accent)}
.item small{display:block;color:var(--dim);font-size:11px;margin-top:2px}

/* ---------- main ---------- */
#main{grid-area:main;overflow:auto;min-width:0}
.view{display:none;height:100%}
.view.on{display:block}

/* ---------- flow view ---------- */
#flowwrap{max-width:900px;margin:0 auto;padding:22px 24px 40px}
#hero{background:linear-gradient(135deg,#1a2740,#151922);
      border:1px solid #2c3d5e;border-radius:12px;padding:20px 22px;margin-bottom:10px}
#hero .lbl{font-size:11px;text-transform:uppercase;letter-spacing:.09em;
           color:var(--accent);font-weight:700;margin-bottom:7px}
#hero h2{font-size:20px;margin-bottom:6px}
#hero p{color:var(--dim);margin-bottom:15px;max-width:60ch}
#progress{display:flex;gap:5px;margin:16px 0 20px}
.pbar{flex:1;height:5px;border-radius:99px;background:var(--panel2)}
.pbar.done{background:var(--ok)}
.pbar.now{background:var(--accent)}
.pbar.fail{background:var(--bad)}

.step{display:grid;grid-template-columns:38px 1fr auto;gap:14px;
      background:var(--panel);border:1px solid var(--line);border-radius:10px;
      padding:15px 17px;margin-bottom:9px;align-items:start}
.step.next{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.step.locked{opacity:.55}
.num{width:30px;height:30px;border-radius:50%;background:var(--panel2);
     display:flex;align-items:center;justify-content:center;font-weight:700;
     font-size:13px;color:var(--dim)}
.num.done{background:var(--ok);color:#06281a}
.num.now{background:var(--accent);color:#fff}
.num.fail{background:var(--bad);color:#fff}
.step h3{font-size:14px;margin-bottom:3px}
.step .what{color:var(--dim);font-size:12.5px;max-width:64ch}
.step .meta{margin-top:7px;font-size:11.5px}
.opt{font-size:10.5px;text-transform:uppercase;letter-spacing:.06em;
     color:var(--dim);border:1px solid var(--line);border-radius:99px;
     padding:1px 7px;margin-left:7px;vertical-align:2px}
.note{margin-top:8px;font-size:12px;border-radius:6px;padding:7px 10px}
.note.block{background:#2a1c1e;color:#f3a2a5}
.note.warn{background:#2c2418;color:#f0c48a}
.note.ok{background:#14261f;color:#8fe3bd}
.sideact{display:flex;flex-direction:column;gap:6px;align-items:stretch;min-width:120px}

#dropzone{border:1.5px dashed var(--line);border-radius:8px;text-align:center;
          padding:16px;color:var(--dim);margin-top:10px;font-size:12.5px;cursor:pointer}
#dropzone.hot{border-color:var(--accent);color:var(--txt)}
#avatarlist{margin-top:8px;display:flex;flex-wrap:wrap;gap:5px}

/* ---------- video view ---------- */
#videowrap{height:100%;display:flex;flex-direction:column;background:#07090d}
#screen{flex:1;display:flex;align-items:center;justify-content:center;padding:16px;min-height:0}
#screen video{max-width:100%;max-height:100%;border-radius:8px;background:#000;
              box-shadow:0 6px 26px #0009}
#placeholder{color:var(--dim);text-align:center;max-width:440px}
#placeholder h2{font-size:16px;margin-bottom:8px;color:var(--txt)}
#transport{display:flex;align-items:center;gap:12px;padding:9px 16px;
           background:var(--panel);border-top:1px solid var(--line)}
#tc{font-family:ui-monospace,Menlo,monospace;font-size:12px;color:var(--dim)}

/* ---------- timeline view ---------- */
#tlview{display:grid;grid-template-columns:minmax(0,1fr) 300px;height:100%}
#tlleft{display:flex;flex-direction:column;min-width:0;overflow:hidden}
#tlbar{display:flex;align-items:center;gap:10px;padding:8px 14px;
       border-bottom:1px solid var(--line);background:var(--panel)}
#tlscroll{overflow:auto;flex:1}
#tlinner{position:relative;min-width:100%}
.ruler{height:22px;position:relative;border-bottom:1px solid var(--line);background:var(--track)}
.tick{position:absolute;top:0;height:100%;border-left:1px solid var(--line);
      padding-left:4px;font-size:10px;color:var(--dim);line-height:22px}
.track{position:relative;height:46px;border-bottom:1px solid var(--line);background:var(--track)}
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
.cue{position:absolute;top:8px;width:2px;height:18px;background:var(--accent2);border-radius:1px}
.cue::after{content:'';position:absolute;top:-4px;left:-2px;width:6px;height:6px;
     border-radius:50%;background:var(--accent2)}
#playhead{position:absolute;top:0;bottom:0;width:2px;background:var(--bad);
     z-index:4;pointer-events:none;left:88px}
#inspect{background:var(--panel);border-left:1px solid var(--line);overflow:auto;padding:14px}
#inspect h3{font-size:12px;text-transform:uppercase;letter-spacing:.07em;
            color:var(--dim);margin-bottom:10px}
.field{margin-bottom:11px}
.field label{display:block;font-size:11px;color:var(--dim);margin-bottom:4px}
.pill{display:inline-block;font-size:11px;padding:2px 8px;border-radius:99px;
      background:var(--panel2);color:var(--dim);margin:0 4px 4px 0}

/* ---------- console drawer ---------- */
#drawer{grid-area:drawer;background:var(--panel);border-top:1px solid var(--line)}
#conbar{display:flex;align-items:center;gap:10px;padding:6px 14px;font-size:11.5px}
#console{background:#080a0f;height:190px;overflow:auto;padding:10px 14px;
         white-space:pre-wrap;font-family:ui-monospace,Menlo,monospace;
         font-size:11.5px;color:#c6d0e0;border-top:1px solid var(--line)}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;background:var(--dim)}
.dot.run{background:var(--accent);animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.3}}
</style></head><body>

<div id="app">
  <div id="top">
    <h1>🎬 Video Editor</h1>
    <div class="sep"></div>
    <div id="tabs">
      <button class="on" data-tab="flow" onclick="showTab('flow')">Steps</button>
      <button data-tab="timeline" onclick="showTab('timeline')">Timeline</button>
      <button data-tab="video" onclick="showTab('video')">Video</button>
    </div>
    <div class="sep"></div>
    <span class="dot" id="jobdot"></span>
    <span id="jobstate" class="dim" style="font-size:12px"></span>
    <button id="stopBtn" class="danger hide" onclick="stopJob()">■ Stop</button>
    <div style="flex:1"></div>
    <span id="health" class="dim" style="font-size:11px"></span>
  </div>

  <div id="bins">
    <div class="binhead">Your videos</div>
    <div id="projlist"></div>
    <div class="binhead">Start a new one</div>
    <input id="newTopic" placeholder="e.g. Millikan oil drop" style="font-size:12px">
    <div class="row" style="margin-top:6px">
      <select id="newLang" style="font-size:12px">
        <option value="hinglish">Hinglish</option>
        <option value="english">English</option>
      </select>
      <button class="primary" onclick="createProject()">Create</button>
    </div>
    <p class="dim" style="font-size:11.5px;margin-top:9px">
      Type a topic and press Create. Then just follow the numbered steps.</p>
  </div>

  <div id="main">
    <div class="view on" id="view-flow"><div id="flowwrap">
      <div id="hero"></div>
      <div id="progress"></div>
      <div id="steps"></div>
    </div></div>

    <div class="view" id="view-timeline"><div id="tlview">
      <div id="tlleft">
        <div id="tlbar">
          <strong style="font-size:12px">Timeline</strong>
          <span class="dim" id="tlinfo"></span>
          <div style="flex:1"></div>
          <span class="dim" style="font-size:11px">zoom</span>
          <input type="range" id="zoom" min="6" max="90" value="26" style="width:130px">
        </div>
        <div id="tlscroll"><div id="tlinner"></div></div>
      </div>
      <div id="inspect"><h3>Inspector</h3>
        <p class="dim">Click any clip in the timeline to edit what it says.</p></div>
    </div></div>

    <div class="view" id="view-video"><div id="videowrap">
      <div id="screen"><div id="placeholder">
        <h2>No video selected</h2><p>Pick one on the left, or create a new one.</p>
      </div></div>
      <div id="transport">
        <button onclick="playPause()" id="playBtn">▶</button>
        <span id="tc">00:00 / 00:00</span>
        <div style="flex:1"></div>
        <span class="dim" id="srcLabel"></span>
        <button id="dlBtn" class="hide" onclick="downloadCut()">⤓ Download</button>
      </div>
    </div></div>
  </div>

  <div id="drawer">
    <div id="conbar">
      <strong>Activity log</strong><span class="dim" id="conhint">idle</span>
      <div style="flex:1"></div>
      <button onclick="toggleConsole()" id="conToggle" style="font-size:11px">show</button>
    </div>
    <pre id="console" class="hide">ready.</pre>
  </div>
</div>

<script>
/* Each step is one pipeline stage, described in what it does for the user
   rather than what it is called internally. `needs` gates the button so a
   newcomer cannot run things out of order; `warn` still allows it. */
const FLOW = [
  {key:'script', n:1, name:'Write the script',
   what:'Drafts the narration, the beats and any equations from your topic. Read it after and fix the wording.',
   makes:'script.md'},
  {key:'narrate', n:2, name:'Record the narration',
   what:'Speaks every line out loud with ElevenLabs. This also decides how long each beat lasts, so everything after follows its timing.',
   makes:'one audio file per beat'},
  {key:'background', n:3, name:'Render the animation',
   what:'Draws the maths with Manim and paints the flat green area where the presenter will stand. This is the slow step.',
   makes:'the background video'},
  {key:'briefs', n:4, name:'List the presenter clips you need', optional:true,
   what:'Writes out exactly which presenter clips to record or generate, and what each should say.',
   makes:'a briefs file'},
  {key:'avatar', n:5, name:'Add the presenter clips',
   what:'Fetches clips from HeyGen, or picks up the green-screen clips you drop in below.',
   makes:'presenter clips'},
  {key:'qc', n:6, name:'Check the quality', optional:true,
   what:'Looks at real rendered frames for cut-off equations, broken maths, typos, or content straying into the presenter area.',
   makes:'a QC report'},
  {key:'composite', n:7, name:'Make the final video',
   what:'Removes the green screen from the presenter and lays them over the animation, then adds the narration.',
   makes:'the final video'},
];

let current=null, proj=null, tl=null, sel=null, es=null, job=null, pps=26,
    projects=[], avatars=[], tab='flow';

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

function showTab(t){
  tab = t;
  document.querySelectorAll('#tabs button').forEach(b=>
    b.classList.toggle('on', b.dataset.tab===t));
  document.querySelectorAll('.view').forEach(v=>
    v.classList.toggle('on', v.id==='view-'+t));
  if(t==='timeline') drawTimeline();
}

/* ---------------- projects ---------------- */
async function loadProjects(){
  projects = await api('/projects');
  $('projlist').innerHTML = projects.map(p=>`
    <div class="item ${p.slug===current?'sel':''}" onclick="openProject('${p.slug}')">
      ${esc(p.title)}<small>${p.has_final?'✅ finished':p.has_background?'animation done':'not started'}</small>
    </div>`).join('') || '<p class="dim" style="font-size:12px">None yet — create one below.</p>';
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
  proj = await api('/projects/'+slug);
  avatars = proj.avatars || [];
  renderFlow();
  loadMonitor(proj);
  await loadTimeline();
  const j = await api('/projects/'+slug+'/job');
  if(j.job && !j.done){ job=j.job; setRunning(j.stage); attach(j.job,0); }
  else setRunning(null);
}

/* ---------------- the flow ---------------- */
function statusOf(key){
  const st = (proj && proj.state && proj.state.stages) || {};
  if(key==='briefs') return (st.avatar||{}).briefs ? 'done' : 'pending';
  return (st[key]||{}).status || 'pending';
}

function blockedReason(step){
  if(!proj) return 'Pick or create a video first';
  if(step.key!=='script' && statusOf('script')!=='done')
    return 'Do step 1 first — everything reads the script.';
  if((step.key==='qc'||step.key==='composite') && statusOf('background')!=='done')
    return 'Do step 3 first — there are no rendered frames yet.';
  if(step.key==='composite' && !avatars.length)
    return 'Do step 5 first — there is no presenter to lay on top.';
  return null;
}

function warnFor(step){
  if(step.key==='background' && statusOf('narrate')!=='done')
    return 'Tip: do step 2 first. The narration decides how long each beat is, so rendering before it may need a re-render.';
  return null;
}

function renderFlow(){
  if(!proj){
    $('hero').innerHTML = `<div class="lbl">Start here</div>
      <h2>No video open</h2>
      <p>Pick one from the left, or type a topic and press Create. Then work down the numbered steps — each one tells you what it does and when it is ready.</p>`;
    $('progress').innerHTML=''; $('steps').innerHTML=''; return;
  }

  const done = FLOW.filter(s=>statusOf(s.key)==='done').length;
  const next = FLOW.find(s=>statusOf(s.key)!=='done' && !s.optional && !blockedReason(s));
  const anyFail = FLOW.find(s=>statusOf(s.key)==='failed');

  $('progress').innerHTML = FLOW.map(s=>{
    const st = statusOf(s.key);
    const cls = st==='done'?'done':st==='failed'?'fail':(next&&next.key===s.key)?'now':'';
    return `<div class="pbar ${cls}" title="${esc(s.name)}"></div>`;
  }).join('');

  if(!next){
    $('hero').innerHTML = `<div class="lbl">All done</div>
      <h2>🎉 ${esc(proj.title)} is finished</h2>
      <p>Every step is complete. Open the <b>Video</b> tab to watch it, or download it from there.</p>
      <button class="primary big" onclick="showTab('video')">Watch the video</button>`;
  } else {
    $('hero').innerHTML = `<div class="lbl">Next step · ${done} of ${FLOW.length} done</div>
      <h2>${next.n}. ${esc(next.name)}</h2>
      <p>${esc(next.what)}</p>
      <div class="row">
        <button class="primary big" onclick="run('${next.key}')">▶ Run this step</button>
        <button onclick="run('build')" title="Runs every remaining step back to back">Do everything for me</button>
      </div>
      ${anyFail?`<div class="note block" style="margin-top:12px">Step ${anyFail.n} failed. Open the activity log at the bottom to see why.</div>`:''}`;
  }

  $('steps').innerHTML = FLOW.map(s=>{
    const st = statusOf(s.key);
    const block = blockedReason(s), warn = warnFor(s);
    const isNext = next && next.key===s.key;
    const numCls = st==='done'?'done':st==='failed'?'fail':isNext?'now':'';
    const label = {done:'Done',failed:'Failed',running:'Running…',pending:'Not started'}[st]||st;
    const extra = s.key==='avatar' ? `
      <div id="dropzone" onclick="document.getElementById('avfile').click()">
        Drop your green-screen presenter clips here, or click to choose files
      </div>
      <input type="file" id="avfile" multiple accept="video/*" class="hide" onchange="uploadFiles(this.files)">
      <div id="avatarlist">${avatars.length
        ? avatars.map(a=>`<span class="pill mono">${esc(a)}</span>`).join('')
        : '<span class="dim" style="font-size:12px">No clips added yet.</span>'}</div>` : '';

    return `<div class="step ${isNext?'next':''} ${block?'locked':''}">
      <div class="num ${numCls}">${st==='done'?'✓':s.n}</div>
      <div>
        <h3>${esc(s.name)}${s.optional?'<span class="opt">optional</span>':''}</h3>
        <div class="what">${esc(s.what)}</div>
        <div class="meta dim">Produces: ${esc(s.makes)} · <b>${label}</b></div>
        ${block?`<div class="note block">🔒 ${esc(block)}</div>`:''}
        ${!block&&warn?`<div class="note warn">${esc(warn)}</div>`:''}
        ${extra}
      </div>
      <div class="sideact">
        <button class="${isNext?'primary':''}" ${block?'disabled':''}
                onclick="run('${s.key}')">${st==='done'?'Run again':'Run'}</button>
        ${s.key==='qc'&&st==='done'?`<button onclick="showTab('timeline')">See findings</button>`:''}
        ${s.key==='composite'&&st==='done'?`<button onclick="showTab('video')">Watch</button>`:''}
      </div>
    </div>`;
  }).join('');

  if(current) wireDrop();
}

/* ---------------- monitor ---------------- */
function loadMonitor(p){
  const which = p.has_final ? 'final' : p.has_background ? 'background' : null;
  $('srcLabel').textContent = which==='final' ? 'final cut (with presenter)'
                            : which==='background' ? 'animation only (no presenter yet)' : '';
  $('dlBtn').classList.toggle('hide', !which);
  if(!which){
    $('screen').innerHTML = `<div id="placeholder"><h2>${esc(p.title)}</h2>
      <p class="dim">Nothing rendered yet. Go to the <b>Steps</b> tab and run step 3.</p></div>`;
    return;
  }
  $('screen').innerHTML =
    `<video id="vid" controls src="/api/projects/${p.slug}/video/${which}"></video>`;
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
  const inner = $('tlinner'); if(!inner) return;
  if(!tl || tl.error || !tl.clips.length){
    inner.innerHTML = `<p class="dim" style="padding:16px">${
      tl && tl.error ? 'Script problem: '+esc(tl.error)
                     : 'No beats yet — run step 1 to write a script.'}</p>`;
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
    <div class="field"><label>Spoken line (read aloud — words only, no symbols)</label>
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
  document.querySelectorAll('.step button, #hero button').forEach(b=>b.disabled=!!stage);
  $('stopBtn').classList.toggle('hide', !stage);
  $('jobdot').classList.toggle('run', !!stage);
  const nice = (FLOW.find(s=>s.key===stage)||{}).name || stage;
  $('jobstate').textContent = stage ? `Running: ${nice}…` : '';
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
  if(!current){ alert('Create or pick a video first.'); return; }
  const con = $('console');
  con.textContent=''; con.classList.remove('hide');
  $('conToggle').textContent='hide';
  try{
    const r = await api(`/projects/${current}/run/${stage}`,{method:'POST'});
    if(!r.started) con.textContent =
      `${r.stage} is already running — showing that job instead.\n`;
    setRunning(r.stage); attach(r.job,0);
  }catch(e){ con.textContent = 'could not start: '+e.message; }
}
async function stopJob(){ if(job) await api(`/jobs/${job}/stop`,{method:'POST'}); }
function toggleConsole(){
  const c=$('console'); const hidden=c.classList.toggle('hide');
  $('conToggle').textContent = hidden?'show':'hide';
}

/* ---------------- uploads ---------------- */
async function uploadFiles(files){
  if(!files || !files.length || !current) return;
  const d=$('dropzone'); const fd=new FormData();
  for(const f of files) fd.append('files',f);
  if(d) d.textContent='uploading…';
  await fetch(`/api/projects/${current}/avatar`,{method:'POST',body:fd});
  openProject(current);
}
function wireDrop(){
  const d=$('dropzone'); if(!d || d.dataset.wired) return;
  d.dataset.wired='1';
  ['dragenter','dragover'].forEach(ev=>d.addEventListener(ev,e=>{
    e.preventDefault(); d.classList.add('hot');}));
  ['dragleave','drop'].forEach(ev=>d.addEventListener(ev,e=>{
    e.preventDefault(); d.classList.remove('hot');}));
  d.addEventListener('drop', e=>{ e.preventDefault(); uploadFiles(e.dataTransfer.files); });
}

/* ---------------- init ---------------- */
$('zoom').addEventListener('input', e=>{ pps=+e.target.value; drawTimeline(); });
api('/health').then(h=>{ $('health').textContent =
  `${h.backend} · ffmpeg ${h.ffmpeg?'ok':'MISSING'}`; });
renderFlow();
loadProjects();
</script></body></html>
"""
