#!/usr/bin/env python3
"""Build one video from an already-shot HeyGen clip: every step of PROCESS.md in
order, each behind its gate, with independent work running at the same time.

    python3 tools/build_clip.py <QID> init            ingest the drop, start work/<slug>/ from work/_template
    python3 tools/build_clip.py <slug> status         every step: done / ready / waiting / blocked / failed
    python3 tools/build_clip.py <slug> plan           the parallel schedule, with serial vs parallel time
    python3 tools/build_clip.py <slug> run            run every machine step that can run, until none can
    python3 tools/build_clip.py <slug> run --dry-run  print the commands instead of running them
    python3 tools/build_clip.py <slug> run --only render --part 2     one step
    python3 tools/build_clip.py <slug> tasks          the writing work that is ready now, as JSON, for agents
    python3 tools/build_clip.py <slug> approve --part 1 [--note "..."]   record the storyboard sign-off

WHY THIS EXISTS
---------------
PROCESS.md's gates all existed before it did, and videos still shipped with the
defects they catch — because each gate was a command someone had to remember to
run, and nothing refused to continue without it. Here a step does not start
until every step it depends on is green, and a green result only counts while
its inputs are unchanged: edit a caption and the retime, the spec, the
storyboard sign-off, the render and the composite all go stale together.

THREE KINDS OF STEP
-------------------
  machine   run by this tool (transcribe, render, composite, the gates)
  author    written by an agent or a person (captions, the design, each SVG) —
            `tasks` lists the ones that are ready, and they are independent, so
            one agent per part and one per diagram can work at the same time
  human     the storyboard sign-off: `approve` records a hash of the exact sheet
            that was looked at, and any change to it withdraws the approval

WHAT RUNS AT THE SAME TIME
--------------------------
Right after ingest, three chains start together: transcription, measuring the
presenter (key + crop), and the question card. The check transcript runs while
the captions are being written, because only the retime gate needs it. Parts
never wait for each other until delivery.

Memory is what limits this on an 8GB machine, not cores: two whisper passes at
once put 3.8GB of model in memory (1.88GB each, measured on CHE-C3-SA-04) and an
earlier two-stream run drove swap to 13.4GB and froze the desktop. So every
step carries its measured memory weight and the scheduler never starts one that
would take the running total past --budget (default 3.0GB, env CLIP_BUDGET_GB).
Before any heavy step, tools/machine_ready.py must pass — the same check
build_one.sh makes — and when it does not, nothing heavy starts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

REPO = Path(__file__).resolve().parents[1]
WORK = REPO / "work"
TEMPLATE = WORK / "_template"
CLIP = REPO / "tools" / "clip"
_VENV = REPO / ".venv-tools" / "bin" / "python"
PY = str(_VENV) if _VENV.exists() else sys.executable   # numpy / scipy tools
def _draw_python() -> str:
    """The interpreter for anything that draws Devanagari: it needs Pillow WITH
    libraqm (or every matra lands after its consonant, silently) and, for
    tools/question_card.py, scipy. The runbook once said "system python3" —
    true when that Pillow alone had libraqm; on 2026-09-21 the tools venv had
    both and the system python had no scipy, so the card step failed. Probe."""
    probe = "from PIL import features; import scipy; raise SystemExit(0 if features.check('raqm') else 1)"
    for py in ([str(_VENV)] if _VENV.exists() else []) + ["python3"]:
        if subprocess.run([py, "-c", probe], capture_output=True).returncode == 0:
            return py
    return "python3"      # make_intro_layers.py refuses loudly without libraqm


PY_DRAW = _draw_python()
BUDGET = float(os.environ.get("CLIP_BUDGET_GB", "3.0"))
HEAVY_GB = 1.0          # at or above this, machine_ready.py must pass first
RENDER_PAGES = int(os.environ.get("CLIP_RENDER_PAGES", "2"))   # browser tabs capturing one part

# Typical wall time per step for a 121s clip. Machine steps are measured:
# CHE-C3-SA-04's logs (2026-09-17), the tools/clip verification renders and
# CHE-C3-SA-06's build (2026-09-21) — render is two tabs with the card drawn in
# (77.6s; one tab without the card was 131s). `plan` scales them by clip
# length. Author times are estimates from one build's file times, and captions
# assume the machine draft (tools/draft_captions.py) is reviewed, not written.
TYPICAL = {
    "ingest": 5, "wav": 4, "transcribe": 140, "transcribe_check": 150, "words": 1,
    "measure": 100, "card": 4, "draft": 2, "captions": 240, "retime": 3, "design": 420,
    "svg": 150, "route": 3, "svgs": 1, "bind": 2, "spec": 8, "storyboard": 11, "approve": 60,
    "render": 78, "composite": 300, "outro": 40,
    "clips": 900, "answer": 0, "deliver": 45, "card_info": 60,
}
SCALES = {"transcribe", "transcribe_check", "render", "composite", "measure", "deliver"}


class GateFailed(Exception):
    pass


# --------------------------------------------------------------------------- video

class Video:
    def __init__(self, slug: str):
        self.slug = slug
        self.dir = WORK / slug
        if not self.dir.is_dir():
            sys.exit(f"no video folder: {self.dir}\nstart it with: python3 tools/build_clip.py <QID> init")
        inputs = self.dir / "inputs.json"
        if not inputs.is_file():
            sys.exit(f"no inputs.json — run: python3 tools/build_clip.py {slug.upper()} init")
        self.inputs = json.loads(inputs.read_text(encoding="utf-8"))
        cfg = self.dir / "video.json"
        if not cfg.is_file():
            sys.exit(f"no video.json in {self.dir} — it names the background; see work/_template/")
        self.cfg = json.loads(cfg.read_text(encoding="utf-8"))
        self.qid = self.inputs["qid"]
        self.parts = {p["part"]: p for p in self.inputs["parts"]}
        self.state_path = self.dir / "state.json"
        self.state = (json.loads(self.state_path.read_text(encoding="utf-8"))
                      if self.state_path.is_file() else {"steps": {}, "approvals": {}})
        self.lock = threading.Lock()

    # paths -----------------------------------------------------------------
    def p(self, rel: str) -> Path:
        return self.dir / rel

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(REPO))
        except ValueError:
            return str(path)

    def clip(self, n: int) -> Path:
        return REPO / self.parts[n]["clip"]["path"]

    def dur(self, n: int) -> float:
        return float(self.parts[n]["clip"]["duration"])

    @property
    def card(self) -> dict | None:
        c = self.cfg.get("card")
        return c if c and c.get("part") else None

    @property
    def last(self) -> int:
        return max(self.parts)

    def record(self, section: str, key: str, value: dict | None):
        """Change ONE entry and save. Several runner processes may share a video
        — a background `run` plus an agent's `run --only` — so a save re-reads
        the file under a lock and merges this entry into it; writing the whole
        in-memory state back would erase whatever the other process recorded."""
        import fcntl
        with self.lock, open(self.state_path.with_suffix(".lock"), "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            disk = (json.loads(self.state_path.read_text(encoding="utf-8"))
                    if self.state_path.is_file() else {"steps": {}, "approvals": {}})
            if value is None:
                disk.setdefault(section, {}).pop(key, None)
            else:
                disk.setdefault(section, {})[key] = value
            tmp = self.state_path.with_suffix(f".tmp{os.getpid()}")
            tmp.write_text(json.dumps(disk, ensure_ascii=False, indent=1), encoding="utf-8")
            os.replace(tmp, self.state_path)
            self.state = disk


# --------------------------------------------------------------------------- hashing

def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def file_sig(p: Path) -> str:
    if p in (REPO, WORK) or p == REPO / "":
        return "UNSET"
    if not p.exists():
        return "MISSING"
    if p.is_dir():
        return hashlib.sha256("".join(f"{c.name}:{file_sig(c)}" for c in sorted(p.iterdir())
                                      if not c.name.startswith(".")).encode()).hexdigest()[:16]
    st = p.stat()
    if st.st_size > 20_000_000:                 # clips: size + mtime, not 130MB of hashing
        return f"{st.st_size}:{st.st_mtime_ns}"
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


# --------------------------------------------------------------------------- steps

@dataclass
class Step:
    name: str
    part: int | None = None
    kind: str = "machine"                        # machine | author | human
    deps: list[str] = field(default_factory=list)
    inputs: list[Path] = field(default_factory=list)
    outputs: list[Path] = field(default_factory=list)
    tools: list[Path] = field(default_factory=list)
    params: dict = field(default_factory=dict)
    gb: float = 0.2
    lock: str | None = None
    action: Callable | None = None
    agent: str | None = None
    brief: str = ""
    sub: str | None = None                       # svg steps: which diagram

    @property
    def key(self) -> str:
        k = self.name if self.part is None else f"{self.name}:{self.part}"
        return f"{k}:{self.sub}" if self.sub else k


ENGINE = sorted((CLIP / "engine").glob("*.*"))
LIB = CLIP / "lib.mjs"
T = lambda *names: [REPO / "tools" / n for n in names]            # noqa: E731


def build_graph(v: Video) -> dict[str, Step]:
    S: dict[str, Step] = {}

    def add(s: Step):
        S[s.key] = s

    add(Step("ingest", inputs=[REPO / v.inputs["drop"]], outputs=[v.p("inputs.json")],
             tools=T("ingest.py"), action=a_ingest))

    card = v.card
    if card:
        missing = [k for k in ("question", "year", "base") if not str(card.get(k, "")).strip()]
        add(Step("card_info", kind="author", deps=["ingest"], agent="you",
                 outputs=[] if not missing else [v.p("video.json#card." + k) for k in missing],
                 brief="fill video.json card.question (the sheet's wording, OCR errors fixed against "
                       "the script), card.year and card.base (the stand-in exam sheet photo)"))
        add(Step("card", deps=["ingest", "card_info"],
                 # the card fields are in params; the whole video.json is not an
                 # input, or the designer setting card.last_cue re-draws the card
                 inputs=[REPO / card["base"]] if card.get("base") else [],
                 outputs=[v.p("assets/question_sheet.png"), v.p("out/layers/ring.png"), v.p("out/plate.png")],
                 # paper_header.py sets the question ON the sheet (question_card
                 # imports it), so a change there redraws the card. Without it
                 # the leading fix of 2026-09-24 left every card green and stale.
                 tools=T("question_card.py", "paper_header.py")
                      + [CLIP / "make_intro_layers.py", CLIP / "plate_frame.mjs",
                        REPO / "src" / "question_card.py", LIB] + ENGINE,
                 params={**{k: card.get(k) for k in ("question", "year", "base", "marks")}, "py": PY_DRAW},
                 gb=0.5, action=a_card))

    for n in sorted(v.parts):
        o = lambda rel: v.p(rel.format(n=n))                        # noqa: E731
        is_card = bool(card) and card["part"] == n
        add(Step("wav", n, deps=["ingest"], inputs=[v.clip(n)], outputs=[o("out/part{n}.wav")],
                 gb=0.2, action=a_wav))
        add(Step("transcribe", n, deps=[f"wav:{n}"], inputs=[o("out/part{n}.wav")],
                 outputs=[o("out/words_part{n}.raw.json"), o("out/words_part{n}.json")],
                 tools=T("silence_cues.py", "word_timings.py"), params={"dur": v.dur(n)},
                 gb=1.9, action=a_transcribe))
        add(Step("words", n, deps=[f"transcribe:{n}"],
                 inputs=[o("out/words_part{n}.json"), o("out/transcript_adjudication_part{n}.json")],
                 action=a_words))
        add(Step("transcribe_check", n, deps=[f"wav:{n}"], inputs=[o("out/part{n}.wav")],
                 outputs=[o("out/words_check_part{n}.json")],
                 tools=T("silence_cues.py", "word_timings.py"), params={"dur": v.dur(n)},
                 gb=1.9, action=a_transcribe_check))
        add(Step("measure", n, deps=["ingest"], inputs=[v.clip(n)],
                 outputs=[o("out/key_part{n}.json"), o("out/crop_part{n}.json")],
                 tools=T("calibrate_key.py", "avatar_crop.py"), gb=0.6, action=a_measure))
        add(Step("draft", n, deps=[f"words:{n}"],
                 inputs=[o("out/words_part{n}.json"), srt_file(v, n)],
                 outputs=[o("out/caption_edit_part{n}.draft.json")],
                 tools=T("draft_captions.py", "align.py"), action=a_draft))
        add(Step("captions", n, kind="author", deps=[f"draft:{n}"], agent="clip-captions",
                 outputs=[o("out/caption_edit_part{n}.json")],
                 brief=f"review out/caption_edit_part{n}.draft.json (every SRT cue already mapped to its "
                       f"words) into out/caption_edit_part{n}.json: notation, flagged splits, keep `cue`"))
        add(Step("retime", n, deps=[f"captions:{n}", f"transcribe_check:{n}", f"words:{n}"],
                 inputs=[o("out/caption_edit_part{n}.json"), o("out/words_part{n}.json"),
                         o("out/words_check_part{n}.json"), o("out/drift_adjudication_part{n}.json")],
                 outputs=[o("out/lines_part{n}.json"), o("out/lines_part{n}.srt")],
                 tools=T("lines_from_edit.py", "srt_drift.py", "align.py"),
                 params={"dur": v.dur(n)}, action=a_retime))
        # The design is a decision about the SCRIPT, so it starts the moment the
        # drop lands — beats name SRT cues and spoken words, not measured times —
        # and runs while the clip is still being transcribed. `bind` attaches it
        # to the clock once the captions are measured.
        add(Step("design", n, kind="author", deps=["ingest"], agent="clip-designer",
                 outputs=[o("spec/parts/design_part{n}.json"), o("spec/route_part{n}.json")],
                 brief=f"design part {n} from the script and the SRT: beats anchored by SRT cue "
                       f"numbers and spoken words (design_part{n}.json), and each beat's route "
                       f"(route_part{n}.json)"))
        add(Step("route", n, deps=[f"design:{n}"],
                 inputs=[o("spec/parts/design_part{n}.json"), o("spec/route_part{n}.json")],
                 tools=T("route_gate.py"), action=a_route))

        # one author step per diagram the design names — these are the work
        # that parallelises best: each SVG is independent of every other
        svg_keys = []
        for asset, beat in diagrams(v, n):
            s = Step("svg", n, kind="author", deps=[f"route:{n}"], agent="clip-svg",
                     outputs=[v.p(asset)], sub=Path(asset).stem,
                     brief=f"draw {asset} for beat {beat.get('type')!r}: "
                           f"{(beat.get('_why') or '')[:300]}")
            add(s)
            svg_keys.append(s.key)
        add(Step("svgs", n, deps=[f"route:{n}"] + svg_keys,
                 inputs=[o("spec/parts/design_part{n}.json")] + [v.p(a) for a, _ in diagrams(v, n)],
                 tools=[CLIP / "svg_lint.py"], action=a_svgs))

        add(Step("bind", n, deps=[f"retime:{n}", f"route:{n}"],
                 inputs=[o("spec/parts/design_part{n}.json"), o("spec/parts/anchors_part{n}.json"),
                         o("out/caption_edit_part{n}.json"), o("out/lines_part{n}.json"),
                         o("out/words_part{n}.json"), v.p("video.json")],
                 outputs=[o("spec/parts/bound/design_part{n}.json"), o("spec/parts/bound/anchors_part{n}.json"),
                          v.p("spec/design.json"), v.p("spec/anchors.json")],
                 tools=T("bind_design.py", "merge_design.py", "check_labels.py", "align.py"),
                 lock="merge", action=a_bind))

        spec_in = [o("spec/parts/bound/design_part{n}.json"), o("spec/parts/bound/anchors_part{n}.json"),
                   o("spec/parts/bound/meta_part{n}.json"),
                   o("out/lines_part{n}.json"), o("out/words_part{n}.json"), v.p("video.json"),
                   v.p("theme.css")] + [v.p(a) for a, _ in diagrams(v, n)]
        add(Step("spec", n, deps=[f"bind:{n}", f"svgs:{n}"], inputs=spec_in,
                 outputs=[o("spec/segments_part{n}.json"), o("out/windows_part{n}.json"),
                          o("out/big_part{n}.json"), o("out/layout_part{n}.json")],
                 tools=T("build_spec.py", "dash_gate.py") + [CLIP / "validate.py", CLIP / "qa.mjs", LIB] + ENGINE,
                 params={"dur": v.dur(n), "card": is_card, "card_last": card.get("last_line") if is_card else None,
                         "layout": v.cfg.get("layout"), "suppress": v.cfg.get("suppress_captions") or []},
                 gb=0.5, action=a_spec))
        add(Step("storyboard", n, deps=[f"spec:{n}"],
                 inputs=[o("spec/segments_part{n}.json"), v.p("video.json"), v.p("theme.css")]
                        + [v.p(a) for a, _ in diagrams(v, n)],
                 outputs=[o("out/storyboard_part{n}.png")],
                 tools=[CLIP / "sheet.mjs", LIB] + ENGINE, gb=0.5, action=a_storyboard))
        add(Step("approve", n, kind="human", deps=[f"storyboard:{n}"],
                 inputs=[o("out/storyboard_part{n}.png")]))

        veo = generated_beats(v, n)
        if veo:
            add(Step("clips", n, kind="author", deps=[f"approve:{n}"], agent="flow (src/veo.py)",
                     outputs=[o("out/clips_part{n}.json")],
                     brief=f"generate and grade the {len(veo)} Veo clip(s) of part {n}: {', '.join(veo)}"))

        # The question card is drawn by the same browser, in the same frames, as
        # the render. It used to be a separate 1080x1344 video laid over the
        # render by ffmpeg — a whole extra encode of the part (35s) to change
        # its first eight seconds, and one more generation of compression.
        add(Step("render", n, deps=[f"approve:{n}", f"spec:{n}"] + (["card"] if is_card else []),
                 inputs=spec_in + [o("spec/segments_part{n}.json"), plate_file(v)]
                        + ([v.p("out/plate.png"), v.p("out/layers")] if is_card else []),
                 outputs=[o("out/render-part{n}.mp4")] + ([o("out/card_part{n}.json")] if is_card else []),
                 tools=[CLIP / "full.mjs", LIB] + ENGINE, params={"card": is_card, "pages": RENDER_PAGES},
                 gb=1.5, action=a_render))
        comp_deps = [f"render:{n}", f"measure:{n}", f"spec:{n}"] + ([f"clips:{n}"] if veo else [])
        add(Step("composite", n, deps=comp_deps,
                 inputs=[o("out/render-part{n}.mp4"), v.clip(n),
                         o("out/key_part{n}.json"), o("out/crop_part{n}.json"),
                         o("out/windows_part{n}.json"), o("out/big_part{n}.json"),
                         o("out/card_part{n}.json"), o("out/layout_part{n}.json"),
                         o("out/clips_part{n}.json")],
                 outputs=[o("out/part{n}-composited.mp4")],
                 tools=T("composite.py") + [REPO / "src" / "panel_layout.py"],
                 params={"card": is_card, "veo": bool(veo)}, gb=1.5, action=a_composite))

    # the answer card closes the LAST part
    ans = v.cfg.get("answer") or {}
    pages = [v.p(x) for x in ans.get("pages", [])]
    deliver_deps = [f"composite:{n}" for n in sorted(v.parts)]
    if ans.get("skip"):
        pass
    elif pages and all(p.exists() for p in pages):
        n = v.last
        add(Step("outro", n, deps=[f"composite:{n}"],
                 inputs=[v.p(f"out/part{n}-composited.mp4"), v.p(f"out/render-part{n}.mp4")] + pages,
                 outputs=[v.p(f"out/part{n}-outro.mp4")],
                 tools=T("answer_outro.py", "plate_from_render.py"), gb=1.0, action=a_outro))
        deliver_deps.append(f"outro:{n}")
    else:
        add(Step("answer", v.last, kind="author", deps=["ingest"], agent="endscreenshot skill",
                 outputs=pages or [v.p("video.json#answer.pages")],
                 brief="the answer page image(s): list them in video.json answer.pages, or set "
                       "answer.skip to the reason (\"user: skip the end answer sheet for now\")"))
        deliver_deps.append(f"answer:{v.last}")
    add(Step("deliver", deps=deliver_deps,
             inputs=[v.p(f"out/part{n}-composited.mp4") for n in v.parts]
                    + [v.p(f"out/part{v.last}-outro.mp4")],
             tools=T("output_gate.py", "sync_check.py"), gb=0.8, action=a_deliver))
    return S


def srt_file(v: Video, n: int) -> Path:
    c = v.parts[n].get("captions") or {}
    return REPO / c["path"] if c.get("path") else v.p("inputs.json")


def plate_file(v: Video) -> Path:
    bg = v.cfg.get("background") or ""
    if not bg:
        return v.p("video.json")
    return v.p(bg) if v.p(bg).exists() else REPO / bg


def diagrams(v: Video, n: int) -> list[tuple[str, dict]]:
    f = v.p(f"spec/parts/design_part{n}.json")
    if not f.is_file():
        return []
    try:
        beats = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    seen, out = set(), []
    for b in beats:
        a = (b.get("diagram") or {}).get("asset")
        if a and a not in seen:
            seen.add(a)
            out.append((a, b))
    return out


def generated_beats(v: Video, n: int) -> list[str]:
    f = v.p(f"spec/route_part{n}.json")
    if not f.is_file():
        return []
    data = json.loads(f.read_text(encoding="utf-8"))
    beats = data["beats"] if isinstance(data, dict) else data
    return [b.get("slug", "?") for b in beats if b.get("route") in ("veo", "generated", "flow")]


# --------------------------------------------------------------------------- status

class Engine:
    def __init__(self, v: Video):
        self.v = v
        self.S = build_graph(v)
        self._fp: dict[str, str] = {}
        self.assume_done: set[str] = set()      # dry-run: steps printed as if they had passed

    def fingerprint(self, s: Step) -> str:
        if s.key in self._fp:
            return self._fp[s.key]
        h = hashlib.sha256()
        for d in s.deps:
            h.update(f"{d}={self.done_fp(d)}".encode())
        for p in sorted(set(s.inputs), key=str):
            h.update(f"{p}={file_sig(p)}".encode())
        for p in sorted(set(s.tools), key=str):
            h.update(f"{p.name}={file_sig(p)}".encode())
        h.update(json.dumps(s.params, sort_keys=True, ensure_ascii=False).encode())
        fp = h.hexdigest()[:16]
        self._fp[s.key] = fp
        return fp

    def done_fp(self, key: str) -> str:
        s = self.S.get(key)
        if s is None:
            return "none"
        if s.kind == "machine":
            return self.fingerprint(s)
        if s.kind == "human":
            a = self.v.state["approvals"].get(key)
            return a["hash"] if a else "none"
        return "|".join(file_sig(Path(str(p).split("#")[0])) for p in s.outputs)

    def outputs_ok(self, s: Step) -> bool:
        for p in s.outputs:
            ps = str(p)
            if "#" in ps:                   # a video.json field still to be filled
                return False
            if not p.exists() or (p.is_file() and p.stat().st_size == 0):
                return False
        return True

    def status(self, key: str, memo: dict | None = None) -> str:
        memo = {} if memo is None else memo
        if key in memo:
            return memo[key]
        s = self.S[key]
        if key in self.assume_done:
            memo[key] = "done"
            return "done"
        deps_ok = all(self.status(d, memo) == "done" for d in s.deps)
        if s.kind == "author":
            # written against inputs that are not green yet counts for nothing:
            # a design built on captions that later fail the retime gate is stale
            st = ("done" if self.outputs_ok(s) else "ready") if deps_ok else "blocked"
        elif s.kind == "human":
            a = self.v.state["approvals"].get(key)
            sheet = s.inputs[0]
            if not deps_ok:
                st = "blocked"
            elif a and sheet.exists() and a["hash"] == file_sig(sheet):
                st = "done"
            else:
                st = "waiting"
        else:
            rec = self.v.state["steps"].get(key)
            if not deps_ok:
                st = "blocked"
            else:
                fp = self.fingerprint(s)
                if rec and rec.get("fp") == fp and rec["status"] == "done" and self.outputs_ok(s):
                    st = "done"
                elif rec and rec.get("fp") == fp and rec["status"] == "failed":
                    st = "failed"
                elif rec and rec["status"] == "done":
                    st = "stale"
                else:
                    st = "ready"
        memo[key] = st
        return st

    def all_status(self) -> dict[str, str]:
        memo: dict[str, str] = {}
        return {k: self.status(k, memo) for k in self.S}


# --------------------------------------------------------------------------- running

class Ctx:
    def __init__(self, v: Video, s: Step, dry: bool):
        self.v, self.s, self.dry = v, s, dry
        logs = v.p("out/logs")
        self.log = logs / f"{s.key.replace(':', '-')}.log"
        if not dry:
            logs.mkdir(parents=True, exist_ok=True)
            self.log.write_text(f"# {s.key}  {datetime.now():%Y-%m-%d %H:%M:%S}\n", encoding="utf-8")

    def sh(self, cmd: list, what: str | None = None, ok=(0,), env: dict | None = None) -> int:
        # repo-relative: the commands run from REPO, and the log reads like the build logs do
        cmd = [self.v.rel(c) if isinstance(c, Path) else str(c) for c in cmd]
        line = " ".join(q(c) for c in cmd)
        if self.dry:
            print(f"      $ {line}")
            return 0
        e = dict(os.environ, PYTHONPATH=str(REPO), **(env or {}))
        with open(self.log, "a", encoding="utf-8") as fh:
            fh.write(f"\n$ {line}\n")
            fh.flush()
            rc = subprocess.run(cmd, cwd=REPO, stdout=fh, stderr=subprocess.STDOUT, env=e).returncode
            fh.write(f"# exit {rc}\n")
        if what is not None and rc not in ok:
            raise GateFailed(f"{what} (exit {rc}) — see {self.v.rel(self.log)}")
        return rc

    def note(self, msg: str):
        if self.dry:
            print(f"      # {msg}")
            return
        with open(self.log, "a", encoding="utf-8") as fh:
            fh.write(f"# {msg}\n")

    def tail(self, n=40) -> str:
        try:
            return "\n".join(self.log.read_text(encoding="utf-8").splitlines()[-n:])
        except OSError:
            return ""


def q(s: str) -> str:
    return s if re.fullmatch(r"[\w./=:,+@%-]+", s) else "'" + s.replace("'", "'\\''") + "'"


def machine_ready() -> str | None:
    r = subprocess.run([sys.executable, str(REPO / "tools" / "machine_ready.py")],
                       capture_output=True, text=True, cwd=REPO)
    return None if r.returncode == 0 else (r.stdout + r.stderr).strip()


def run(v: Video, only: str | None, part: int | None, dry: bool, budget: float, retry: bool = False) -> int:
    eng = Engine(v)
    targets = None
    if only:
        targets = {k for k, s in eng.S.items() if s.name == only and (part is None or s.part == part)}
        if not targets:
            sys.exit(f"no step {only!r}" + (f" for part {part}" if part else ""))
    running: dict = {}
    used = 0.0
    started_at: dict[str, float] = {}
    results: list[tuple[str, str, float]] = []
    held_back = None
    t_all = time.time()
    pool = ThreadPoolExecutor(max_workers=8)
    locks: set[str] = set()
    retried: set[str] = set()                   # --retry runs a failed step once, not forever

    def launch(s: Step):
        ctx = Ctx(v, s, dry)
        print(f"  > {s.key:<24} starting" + (f"  ({s.gb:.1f}GB)" if s.gb >= HEAVY_GB else ""))
        if dry:
            s.action(v, s, ctx)
            return None
        return pool.submit(execute, v, s, ctx)

    while True:
        eng._fp.clear()
        st = eng.all_status()
        # --retry: a step that failed on these exact inputs is run again — for
        # when the fix was to the machine (a missing module), not to an input
        again = ("ready", "stale", "failed") if retry else ("ready", "stale")
        ready = [eng.S[k] for k, x in st.items()
                 if x in again and eng.S[k].kind == "machine" and k not in retried
                 and k not in running and (targets is None or k in targets)]
        ready.sort(key=lambda s: -critical(eng, s.key))
        for s in ready:
            if dry:
                launch(s)
                eng.assume_done.add(s.key)
                continue
            if s.lock and s.lock in locks:
                continue
            if used + s.gb > budget and running:
                continue
            if s.gb >= HEAVY_GB:
                why = machine_ready()
                if why:
                    held_back = why
                    continue
            f = launch(s)
            retried.add(s.key)
            # so `status` from another shell can say what is running right now
            v.record("running", s.key, {"pid": os.getpid(), "since": datetime.now().isoformat(timespec="seconds")})
            running[s.key] = (f, s)
            used += s.gb
            started_at[s.key] = time.time()
            if s.lock:
                locks.add(s.lock)
        if dry:
            if not ready:
                break
            continue
        if not running:
            break
        done, _ = wait([f for f, _ in running.values()], return_when=FIRST_COMPLETED)
        for key in [k for k, (f, _) in running.items() if f in done]:
            f, s = running.pop(key)
            v.record("running", key, None)
            used -= s.gb
            if s.lock:
                locks.discard(s.lock)
            ok, msg = f.result()
            secs = time.time() - started_at[key]
            eng._fp.clear()
            v.record("steps", key, {"status": "done" if ok else "failed", "fp": eng.fingerprint(s),
                                    "secs": round(secs, 1), "at": datetime.now().isoformat(timespec="seconds"),
                                    "log": v.rel(v.p(f"out/logs/{key.replace(':', '-')}.log"))})
            results.append((key, "done" if ok else "FAILED", secs))
            print(f"  {'✓' if ok else 'X'} {key:<24} {secs:6.1f}s" + ("" if ok else f"\n      {msg}"))
    pool.shutdown()
    if dry:
        st = eng.all_status()
        stop = [k for k, x in st.items() if x in ("ready", "waiting") and eng.S[k].kind != "machine"]
        print(f"\n  dry run stops here — waiting on: {', '.join(stop) or 'nothing'}")
        return 0
    wall = time.time() - t_all
    if targets and not results:
        st = eng.all_status()
        for k in sorted(targets):
            waiting = [d for d in eng.S[k].deps if st[d] != "done"]
            print(f"  {k}: {st[k]}" + (f" — needs {', '.join(waiting)}" if waiting else ""))
    if results:
        serial = sum(r[2] for r in results)
        print(f"\n  {len(results)} step(s) in {wall:.0f}s wall — {serial:.0f}s if run one after another")
    if held_back:
        print(f"\n  HELD BACK — heavy steps did not start:\n    {held_back}")
    print()
    show_status(v, brief=True)
    return 1 if any(r[1] == "FAILED" for r in results) else 0


def execute(v: Video, s: Step, ctx: Ctx):
    try:
        s.action(v, s, ctx)
        for p in s.outputs:
            if "#" not in str(p) and not p.exists():
                raise GateFailed(f"did not write {v.rel(p)}")
        return True, ""
    except GateFailed as e:
        ctx.note(f"GATE FAILED: {e}")
        return False, str(e)
    except Exception as e:                                # noqa: BLE001
        ctx.note(f"ERROR: {e!r}")
        return False, f"{e!r} — see {v.rel(ctx.log)}"


def critical(eng: Engine, key: str, memo: dict | None = None) -> float:
    """Longest typical time from this step to delivery: run the long chains first."""
    memo = {} if memo is None else memo
    if key in memo:
        return memo[key]
    kids = [k for k, s in eng.S.items() if key in s.deps]
    s = eng.S[key]
    memo[key] = TYPICAL.get(s.name, 10) + max((critical(eng, k, memo) for k in kids), default=0)
    return memo[key]


# --------------------------------------------------------------------------- actions

def a_ingest(v, s, c):
    c.sh(["python3", "tools/ingest.py", v.qid], "ingest gate")


def a_wav(v, s, c):
    n = s.part
    c.sh(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", v.clip(n), "-vn", "-ac", "1", "-ar", "16000",
          "-c:a", "pcm_s16le", v.p(f"out/part{n}.wav")], "audio extract")


def a_transcribe(v, s, c):
    """The primary transcript, chunked on pauses measured at -35dB/0.25s.

    Written to words_part<N>.raw.json. words_part<N>.json is what every later
    step reads, and it may carry hand corrections made against silences (31 on
    CHE-C3-SA-04) — so it is created from the raw file ONCE and never
    overwritten by a re-run."""
    n = s.part
    wav, sil = v.p(f"out/part{n}.wav"), v.p(f"out/silence_part{n}.srt")
    c.sh(["python3", "tools/silence_cues.py", wav, sil, "--db", "-35", "--min", "0.25"], "silence detect")
    c.sh(["python3", "tools/word_timings.py", wav, sil, v.dur(n), v.p(f"out/words_part{n}.raw.json")],
         "word timings")
    words = v.p(f"out/words_part{n}.json")
    if words.exists():
        c.note(f"kept existing {v.rel(words)} (may carry hand corrections); raw transcript refreshed")
    elif not c.dry:
        shutil.copyfile(v.p(f"out/words_part{n}.raw.json"), words)


def a_transcribe_check(v, s, c):
    """The INDEPENDENT transcript the retime gate measures against: different
    chunk boundaries (-28dB/0.12s), so it is not the captions agreeing with
    themselves. It runs while the captions are being written."""
    n = s.part
    wav, sil = v.p(f"out/part{n}.wav"), v.p(f"out/silence_check_part{n}.srt")
    c.sh(["python3", "tools/silence_cues.py", wav, sil, "--db", "-28", "--min", "0.12"], "silence detect")
    c.sh(["python3", "tools/word_timings.py", wav, sil, v.dur(n), v.p(f"out/words_check_part{n}.json")],
         "word timings (check)")


def adjudicated(v: Video, name: str) -> dict:
    f = v.p(f"out/{name}")
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def a_words(v, s, c):
    """PROCESS.md gate 2: no holes > 1.5s, no collapsed tokens > 1.3s.

    A flagged item passes only when out/transcript_adjudication_part<N>.json
    names it with a reason (a pause the silences confirm; a formula read slowly
    — "2.303R" on CHE-C3-SA-04 legitimately took 2.6s)."""
    n = s.part
    c.note("gate: holes > 1.5s and tokens > 1.3s, each adjudicated or fixed")
    if c.dry:
        return
    w = json.loads(v.p(f"out/words_part{n}.json").read_text(encoding="utf-8"))
    holes = [(float(a["e"]), float(b["s"])) for a, b in zip(w, w[1:]) if float(b["s"]) - float(a["e"]) > 1.5]
    long = [(float(x["s"]), x["w"]) for x in w if float(x["e"]) - float(x["s"]) > 1.3]
    back = [(a["s"], b["s"]) for a, b in zip(w, w[1:]) if float(b["s"]) < float(a["s"])]
    adj = adjudicated(v, f"transcript_adjudication_part{n}.json")
    ok_s = {round(float(x["s"]), 2) for x in adj.get("items", []) if x.get("why")}
    bad = [f"hole {a:.2f}->{b:.2f}" for a, b in holes if round(a, 2) not in ok_s] + \
          [f"token {w_!r} at {t:.2f} lasts > 1.3s" for t, w_ in long if round(t, 2) not in ok_s] + \
          [f"out of order at {a}" for a, _ in back]
    c.note(f"{len(w)} words, {len(holes)} hole(s), {len(long)} long token(s), {len(back)} out of order")
    if bad:
        raise GateFailed("transcript gate: " + "; ".join(bad) +
                         f" — fix with tools/fill_gaps.py, or adjudicate each in "
                         f"out/transcript_adjudication_part{n}.json "
                         '{"items":[{"s": <start>, "why": "..."}]}')


def a_measure(v, s, c):
    n = s.part
    key, crop = v.p(f"out/key_part{n}.json"), v.p(f"out/crop_part{n}.json")
    c.sh([PY, "tools/calibrate_key.py", v.clip(n), key], "key calibration")
    c.sh([PY, "tools/avatar_crop.py", v.clip(n), crop], "presenter crop")
    c.note("gate: key hole <= 0.5% and leak <= 0.5%")
    if not c.dry:
        k = json.loads(key.read_text())
        if k.get("hole", 99) > 0.5 or k.get("leak", 99) > 0.5:
            raise GateFailed(f"key gate: hole {k.get('hole')}% leak {k.get('leak')}% — "
                             "the key punches the face or leaves green; re-shoot or tune calibrate_key")


def a_retime(v, s, c):
    n = s.part
    lines, srt = v.p(f"out/lines_part{n}.json"), v.p(f"out/lines_part{n}.srt")
    c.sh(["python3", "tools/lines_from_edit.py", v.p(f"out/words_part{n}.json"),
          v.p(f"out/caption_edit_part{n}.json"), lines, "--clip-end", v.dur(n)], "caption lines")
    c.note(f"write {v.rel(srt)} from the lines (srt_drift reads SRT)")
    if not c.dry:
        write_srt(json.loads(lines.read_text(encoding="utf-8")), srt)
    rc = c.sh(["python3", "tools/srt_drift.py", srt, v.p(f"out/words_check_part{n}.json"),
               "--tol", "0.35"], None)
    if c.dry:
        return
    out = c.tail(400)
    flagged = set()
    m = re.search(r"drift past [\d.]+s: (\[.*\])", out)
    if m:
        flagged |= {int(x) for x in re.findall(r"\((\d+),", m.group(1))}
    m = re.search(r"below the confidence floor - check by hand: (\[.*\])", out)
    if m:
        flagged |= {int(x) for x in re.findall(r"\d+", m.group(1))}
    adj = adjudicated(v, f"drift_adjudication_part{n}.json")
    judged = {int(x["cue"]) for x in adj.get("cues", []) if x.get("judged") and x.get("evidence")}
    left = sorted(flagged - judged)
    c.note(f"srt_drift exit {rc}; flagged cues {sorted(flagged)}; adjudicated {sorted(judged & flagged)}")
    if rc not in (0, 1) or left or (rc == 1 and not flagged):
        raise GateFailed(f"retime gate: cue(s) {left} drift past 0.35s or are low-confidence and are "
                         f"not adjudicated — fix the caption edit, or record each in "
                         f"out/drift_adjudication_part{n}.json with `judged` and `evidence` measured "
                         f"against silencedetect")


def write_srt(lines: list[dict], out: Path):
    def ts(t):
        ms = int(round(float(t) * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    out.write_text("".join(f"{i}\n{ts(l['start'])} --> {ts(l['end'])}\n{l['text']}\n\n"
                           for i, l in enumerate(lines, 1)), encoding="utf-8")


def a_draft(v, s, c):
    c.sh(["python3", "tools/draft_captions.py", v.slug, s.part], "caption draft")


def a_route(v, s, c):
    c.sh(["python3", "tools/route_gate.py", v.p(f"spec/route_part{s.part}.json")], "route gate")


def a_bind(v, s, c):
    n = s.part
    c.sh(["python3", "tools/bind_design.py", v.slug, n], "bind the design to the measured clock")
    c.sh(["python3", "tools/merge_design.py", v.slug, "--bound"], "merge design")
    c.sh(["python3", "tools/check_labels.py", f"work/{v.slug}", n], "label gate")


def card_last(v: Video, n: int):
    """The card's last caption LINE: set directly (`last_line`), or derived by
    bind_design from the SRT cue the card ends on (`last_cue`)."""
    k = v.card or {}
    if k.get("last_cue"):
        meta = v.p(f"spec/parts/bound/meta_part{n}.json")
        return json.loads(meta.read_text(encoding="utf-8")).get("card_last_line") if meta.is_file() else None
    return k.get("last_line")


def a_svgs(v, s, c):
    c.sh(["python3", CLIP / "svg_lint.py", "--design", v.p(f"spec/parts/design_part{s.part}.json")], "svg gate")


def a_spec(v, s, c):
    n = s.part
    cmd = ["python3", "tools/build_spec.py", v.slug, n, v.dur(n)]
    if s.params["card"]:
        cmd.append("--card")
        last = card_last(v, n) if not c.dry else s.params["card_last"]
        if last is not None:
            cmd.append(f"--card-last={last}")
    if s.params["suppress"]:
        # video.json "suppress_captions": ["equation"] — no caption under those kinds of segment
        cmd.append("--suppress-captions=" + ",".join(s.params["suppress"]))
    c.sh(cmd, "spec build (segments must sum to the clip)")
    c.sh(["python3", CLIP / "validate.py", v.slug, "--part", n], "validate.py")
    c.sh(["node", CLIP / "qa.mjs", v.slug, "--part", n], "qa.mjs")
    c.sh(["python3", "tools/dash_gate.py", f"work/{v.slug}"], "dash gate")
    layout = s.params["layout"] or {"busy_w": 600, "floor": 1210}
    c.note(f"write out/layout_part{n}.json {layout}")
    if not c.dry:
        v.p(f"out/layout_part{n}.json").write_text(json.dumps(layout, separators=(",", ":")))


def a_storyboard(v, s, c):
    c.sh(["node", CLIP / "sheet.mjs", v.slug, "--part", s.part], "storyboard")


def a_render(v, s, c):
    n = s.part
    cmd = ["node", CLIP / "full.mjs", v.slug, "--part", n, "--pages", s.params["pages"]]
    if s.params["card"]:
        cmd.append("--intro")
    c.sh(cmd, "render (text audit)")
    if s.params["card"]:
        d = seg1(v, n) if not c.dry else 0.0
        c.note(f"write out/card_part{n}.json [[-1.0, {d:.3f}]] — starts before 0 so he is card-sized on frame 1")
        if not c.dry:
            v.p(f"out/card_part{n}.json").write_text(json.dumps([[-1.0, round(d, 3)]]))


def a_card(v, s, c):
    k = v.card
    c.sh([PY_DRAW, "tools/question_card.py", "--base", REPO / k["base"], "--question", k["question"],
          "--year", k["year"], "--subject", v.cfg.get("subject", ""), "--out", v.p("assets/question_sheet.png"),
          "--renderer", CLIP / "engine"], "question sheet")
    c.sh([PY_DRAW, CLIP / "make_intro_layers.py", v.slug, k["year"]] + ([k["marks"]] if k.get("marks") else []),
         "intro layers (libraqm)")
    c.sh(["node", CLIP / "plate_frame.mjs", v.slug], "plate frame")


def seg1(v: Video, n: int) -> float:
    return float(json.loads(v.p(f"spec/segments_part{n}.json").read_text(encoding="utf-8"))[0]["duration"])


def a_composite(v, s, c):
    n = s.part
    body = v.p(f"out/render-part{n}.mp4")          # the card is already in it
    opt = lambda rel: v.p(rel) if v.p(rel).exists() else "-"        # noqa: E731
    c.sh([PY, "tools/composite.py", body, v.clip(n), v.p(f"out/key_part{n}.json"),
          v.p(f"out/part{n}-composited.mp4"), v.p(f"out/windows_part{n}.json"), "-",
          opt(f"out/clips_part{n}.json") if s.params["veo"] else "-",
          v.p(f"out/big_part{n}.json"), v.p(f"out/crop_part{n}.json"),
          v.p(f"out/card_part{n}.json") if s.params["card"] else "-",
          v.p(f"out/layout_part{n}.json")], "composite")


def a_outro(v, s, c):
    n = s.part
    plate = v.p(f"out/plate_part{n}.png")
    c.sh(["python3", "tools/plate_from_render.py", v.p(f"out/render-part{n}.mp4"), plate], "median plate")
    pages = [v.p(x) for x in v.cfg["answer"]["pages"]]
    c.sh(["python3", "tools/answer_outro.py", v.p(f"out/part{n}-composited.mp4")] + pages +
         [v.p(f"out/part{n}-outro.mp4"), "--plate-image", plate], "answer outro")


def a_deliver(v, s, c):
    """Gate the file that SHIPS, not the one before it: copy, then check the
    copy. The geometry sidecar travels with it or output_gate cannot check the
    presenter (CHE-C3-SA-04's first delivery failed exactly that way)."""
    final = REPO / "final" / v.qid
    if not c.dry:
        final.mkdir(parents=True, exist_ok=True)
    for n in sorted(v.parts):
        src = v.p(f"out/part{n}-outro.mp4") if (n == v.last and v.p(f"out/part{n}-outro.mp4").exists()) \
            else v.p(f"out/part{n}-composited.mp4")
        name = f"{v.slug}.mp4" if len(v.parts) == 1 else f"{v.slug}-part{n}.mp4"
        dst = final / name
        c.sh([PY, "tools/output_gate.py", src], f"output gate on {src.name}")
        c.note(f"copy {v.rel(src)} (+ .geom.json) -> {v.rel(dst)}, then prove the copy is that file")
        if not c.dry:
            shutil.copyfile(src, dst)
            geo = Path(str(src) + ".geom.json")
            if geo.exists():
                shutil.copyfile(geo, Path(str(dst) + ".geom.json"))
            # The shipped file must be the gated file. A second output_gate
            # decode of the copy proved that at the cost of a full decode; a
            # hash of both proves it exactly, including the sidecar.
            for a_, b_ in ((src, dst), (Path(str(src) + ".geom.json"), Path(str(dst) + ".geom.json"))):
                if a_.exists() and sha(a_) != sha(b_):
                    raise GateFailed(f"{b_.name} is not byte-identical to the gated {a_.name}")
        cmd = [PY, "tools/sync_check.py", v.slug, n, dst]
        if v.p("out/plate.png").exists():
            cmd += ["--plate", "out/plate.png"]      # sync_check reads it relative to the video folder
        if v.card and v.card["part"] == n and not c.dry:
            cmd += ["--skip-until", f"{seg1(v, n):.3f}"]
        c.sh(cmd, f"sync check on delivered {name}")
    # The video ships with the code that made it: final/<QID>/code/.
    code = [v.rel(v.dir)] + ([f"projects/{v.slug}"] if (REPO / "projects" / v.slug).is_dir() else [])
    c.sh(["python3", "tools/archive_code.py", v.qid] + code, "snapshot code into final/")


# --------------------------------------------------------------------------- commands

ICON = {"done": "✓", "ready": "▶", "stale": "↻", "waiting": "…", "blocked": "·", "failed": "X",
        "running": "⟳"}


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def show_status(v: Video, brief=False):
    eng = Engine(v)
    st = eng.all_status()
    for k, r in (v.state.get("running") or {}).items():
        if k in st and st[k] != "done" and _alive(int(r.get("pid", 0))):
            st[k] = "running"
    by_part: dict = {}
    for k, s in eng.S.items():
        by_part.setdefault(s.part, []).append(k)
    for part in sorted(by_part, key=lambda x: (x is not None, x or 0)):
        print(f"  {'video' if part is None else f'part {part}'}")
        for k in by_part[part]:
            s = eng.S[k]
            rec = v.state["steps"].get(k, {})
            extra = f"  {rec['secs']:.0f}s" if st[k] == "done" and rec.get("secs") else ""
            who = f"  [{s.agent}]" if s.kind == "author" and st[k] == "ready" else ""
            if s.kind == "human" and st[k] == "waiting":
                who = f"  look at {v.rel(s.inputs[0])}, then: approve --part {s.part}"
            if st[k] == "failed":
                who = f"  see {rec.get('log', '')}"
            if brief and st[k] == "blocked":
                continue
            print(f"    {ICON[st[k]]} {k:<26} {st[k]:<8}{extra}{who}")
    tasks = [k for k, x in st.items() if x == "ready" and eng.S[k].kind == "author"]
    runnable = [k for k, x in st.items() if x in ("ready", "stale") and eng.S[k].kind == "machine"]
    human = [k for k, x in st.items() if x == "waiting"]
    print()
    if runnable:
        print(f"  machine steps ready ({len(runnable)}): run  python3 tools/build_clip.py {v.slug} run")
    if tasks:
        print(f"  writing ready for {len(tasks)} agent(s) at once: python3 tools/build_clip.py {v.slug} tasks")
    if human:
        print(f"  waiting on a person: {', '.join(human)}")
    if st.get("deliver") == "done":
        print(f"  DELIVERED — final/{v.qid}/")


def show_tasks(v: Video):
    eng = Engine(v)
    st = eng.all_status()
    out = []
    for k, x in st.items():
        s = eng.S[k]
        if s.kind != "author" or x != "ready":
            continue
        out.append({"task": k, "agent": s.agent, "part": s.part, "slug": v.slug,
                    "writes": [v.rel(Path(str(p).split("#")[0])) + ("#" + str(p).split("#")[1] if "#" in str(p) else "")
                               for p in s.outputs],
                    "brief": s.brief})
    print(json.dumps(out, ensure_ascii=False, indent=1))


def approve(v: Video, part: int, note: str | None):
    eng = Engine(v)
    key = f"approve:{part}"
    if key not in eng.S:
        sys.exit(f"no part {part}")
    st = eng.status(key)
    if st == "blocked":
        sys.exit(f"the storyboard for part {part} is not built and green yet — nothing to approve")
    sheet = eng.S[key].inputs[0]
    v.record("approvals", key, {"hash": file_sig(sheet), "at": datetime.now().isoformat(timespec="seconds"),
                                "sheet": v.rel(sheet), "note": note or ""})
    print(f"  approved {v.rel(sheet)} ({file_sig(sheet)}). Any change to that sheet withdraws this.")


def plan(v: Video, budget: float = BUDGET, agents: int = 6):
    """The schedule this runner would actually follow, simulated with the same
    rule the scheduler uses — machine steps share the memory budget, and a step
    starts only when every step it depends on has finished — against running
    the same steps one after another, which is how every video so far was built.

    Step times are TYPICAL (measured on CHE-C3-SA-04), scaled by clip length.
    Author steps are what one build took between files: estimates, not promises."""
    eng = Engine(v)
    scale = max(v.dur(n) for n in v.parts) / 121.0
    dur = {k: TYPICAL.get(s.name, 10) * (scale if s.name in SCALES else 1) for k, s in eng.S.items()}
    memo: dict[str, float] = {}
    prio = {k: critical(eng, k, memo) for k in eng.S}

    t, used, busy_agents = 0.0, 0.0, 0
    start: dict[str, float] = {}
    end: dict[str, float] = {}
    running: dict[str, float] = {}
    while len(end) < len(eng.S):
        for k in sorted((k for k in eng.S if k not in start), key=lambda k: -prio[k]):
            s = eng.S[k]
            if not all(d in end and end[d] <= t for d in s.deps):
                continue
            if s.kind == "machine":
                if used + s.gb > budget and any(eng.S[r].kind == "machine" for r in running):
                    continue
                used += s.gb
            elif s.kind == "author" and s.agent not in ("you",):
                if busy_agents >= agents:
                    continue
                busy_agents += 1
            start[k] = t
            running[k] = t + dur[k]
        if not running:
            sys.exit("plan: nothing can start — a dependency loop")
        k = min(running, key=running.get)
        t = running.pop(k)
        end[k] = t
        s = eng.S[k]
        if s.kind == "machine":
            used -= s.gb
        elif s.kind == "author" and s.agent not in ("you",):
            busy_agents -= 1
        # everything else finishing at the same instant
        for k2 in [x for x, e in running.items() if e <= t]:
            running.pop(k2)
            end[k2] = t
            s2 = eng.S[k2]
            if s2.kind == "machine":
                used -= s2.gb
            elif s2.kind == "author" and s2.agent not in ("you",):
                busy_agents -= 1

    serial = sum(dur.values())
    machine = sum(d for k, d in dur.items() if eng.S[k].kind == "machine")
    print(f"  {v.slug}: {len(v.parts)} part(s), clip {', '.join(f'{v.dur(n):.0f}s' for n in sorted(v.parts))}"
          f" — memory budget {budget}GB, up to {agents} agents at once")
    print(f"  {'step':<26}{'kind':<9}{'starts':>8}{'takes':>8}")
    for k in sorted(eng.S, key=lambda k: (start[k], k)):
        print(f"  {k:<26}{eng.S[k].kind:<9}{start[k]:7.0f}s{dur[k]:7.0f}s")
    total = max(end.values())
    print(f"\n  one after another : {serial / 60:5.1f} min  (machine steps alone {machine / 60:.1f} min)")
    print(f"  this schedule     : {total / 60:5.1f} min  ({serial / total:.1f}x)")


def init(qid: str):
    slug = qid.lower()
    d = WORK / slug
    r = subprocess.run([sys.executable, "tools/ingest.py", qid], cwd=REPO)
    if r.returncode:
        sys.exit("ingest refused the drop — fix inbox/ first")
    if (d / "video.json").exists():
        print(f"  {d.relative_to(REPO)}/video.json exists — design untouched")
        return
    if not TEMPLATE.is_dir():
        sys.exit("no work/_template")
    for src in TEMPLATE.rglob("*"):
        dst = d / src.relative_to(TEMPLATE)
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        elif not dst.exists() and src.name != "README.md":
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
    cfg = json.loads((d / "video.json").read_text(encoding="utf-8"))
    subj = {"che": "chemistry", "phy": "physics", "bio": "biology", "mat": "maths"}.get(slug[:3], "")
    cfg.update({"qid": qid, "slug": slug, "subject": subj})
    plate = REPO / "assets" / "backgrounds" / f"{subj}.png"
    if subj and plate.exists():
        (d / "assets").mkdir(exist_ok=True)
        shutil.copyfile(plate, d / "assets" / f"{subj}-bg.png")
        cfg["background"] = f"assets/{subj}-bg.png"
    (d / "video.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"  started {d.relative_to(REPO)}/ from work/_template — background {cfg.get('background') or 'NOT SET'}")
    show_status(Video(slug))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video", help="QID for init, slug otherwise")
    ap.add_argument("cmd", choices=["init", "status", "plan", "run", "tasks", "approve"])
    ap.add_argument("--part", type=int)
    ap.add_argument("--only", help="run just this step (e.g. render)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--retry", action="store_true", help="also re-run steps that failed on unchanged inputs")
    ap.add_argument("--budget", type=float, default=BUDGET, help="GB of heavy work at once")
    ap.add_argument("--note")
    ap.add_argument("--agents", type=int, default=6, help="plan: agents writing at once")
    a = ap.parse_args()
    if a.cmd == "init":
        init(a.video.upper())
        return 0
    v = Video(a.video.lower())
    if a.cmd == "status":
        show_status(v)
    elif a.cmd == "plan":
        plan(v, a.budget, a.agents)
    elif a.cmd == "tasks":
        show_tasks(v)
    elif a.cmd == "approve":
        if not a.part:
            sys.exit("approve needs --part N")
        approve(v, a.part, a.note)
    elif a.cmd == "run":
        return run(v, a.only, a.part, a.dry_run, a.budget, a.retry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
