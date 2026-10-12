"""Assemble one part of an arts reel from its edit list.

    python3 tools/reel/build_part.py work/<slug>/edit_part<N>.json [bg|comp|stills|all] [--no-captions]

The edit list is DATA and lives in the video folder; this is the build code and
lives here (PROCESS_ARTS.md section 6). It names the HeyGen clip, the measured
key, the background segments, where the presenter is in each scene, and the
layers drawn by the video's design code:

  under.mov     behind him, above the footage (the dark disc of his circle)
  mask.mov      opaque matte: white where he may show (full / circle / none)
  overlay.mov   every tag, card, ring and icon
  captions.mov  the caption line

The clock is his voice: every time is seconds into his clip. A change of
placement is eased with smoothstep over GLIDE seconds CENTRED on its cut, the
same curve the mask layer uses, so he and his circle move as one.

Grown out of docs/history-poc/reel_build.py (the Magadha proof of concept),
which stays where it is as the reference. New here: split-screen segments,
per-cut transition lengths, a vertical placement, and the mask.

Since POL-C3-LA-02 the layers are SPARSE movies (tools/reel/layers.mjs: one PNG
per change, real timestamps), so each is read through `fps=30`, which holds a
picture until the next one. Three optional things in the edit list:

  "hold": true on a segment   a clip shorter than its scene stops on its last
                              frame instead of being slowed (a printed picture
                              may stand still; it may never run backwards)
  "cutout": {"edge": 6, "shadow": true}
                              a white paper edge round the presenter and a soft
                              shadow under him, so he sits ON a page
  "grain": "out/layers/grain.png"
                              one still laid over the page, under him
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FPS = 30
XF = 0.35        # default dissolve; it ENDS at the cut
GLIDE = 0.5      # placement ease, centred on the cut
SLOW_FLOOR = 0.75
VEO_720_CROP = "crop=630:1120:45:0"   # 720x1280 Flow clip -> 9:16, stops above the mark at ~0.9h


def run(cmd):
    print("+", " ".join(str(c) for c in cmd)[:220], flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def picture_length(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip().split("\n")[0])


def gate_length(p, want, what):
    """A track whose PICTURE is shorter than the part is not a finished track: the file's own
    duration is the longer of sound and picture and hides it."""
    got = picture_length(p)
    if abs(got - want) > 0.1:
        raise SystemExit(f"GATE: the picture of {what} is {got:.2f} s, the part is {want:.2f} s ({p})")


def length(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


class Part:
    def __init__(self, edit_path):
        self.path = Path(edit_path).resolve()
        self.dir = self.path.parent
        self.e = json.loads(self.path.read_text(encoding="utf-8"))
        self.n = self.e["part"]
        # the frame rate the part is built at: the edit list's "fps" (from look.json), else 30.
        # GEO-C3-SA-01 runs at its HeyGen clip's own 25: 25 -> 30 shows every fifth frame of him twice.
        global FPS
        FPS = int(self.e.get("fps", 30))
        self.dur = float(self.e["dur"])
        self.out = self.dir / "out"
        (self.out / "tmp").mkdir(parents=True, exist_ok=True)

    def p(self, rel):
        rel = Path(rel)
        if rel.is_absolute():
            return rel
        for base in (self.dir, ROOT):
            if (base / rel).exists():
                return base / rel
        return self.dir / rel

    # ------------------------------------------------------------ background
    def _split(self, seg, i):
        """A top/bottom split screen, rendered to its own clip first."""
        sp = seg["split"]
        d = seg["t1"] - seg["t0"] + 0.4                      # 0.4 s head for the dissolve in
        out = self.out / "tmp" / f"split_p{self.n}_{i}.mp4"
        parts, ins = [], []
        for k, name in enumerate(("top", "bottom")):
            h = sp[name]
            src = self.p(h["src"])
            ins += ["-i", src]
            delay = float(h.get("delay", 0.0))               # held on its first frame until then
            need = d - delay
            st = float(h.get("start", 0.3))
            usable = length(src) - st - 0.1
            ch = f"[{k}:v]trim=start={st}:duration={min(need, usable):.3f},setpts=PTS-STARTPTS"
            if usable < need - 0.02:
                sp_ = usable / need
                if sp_ < SLOW_FLOOR:
                    raise SystemExit(f"split {name}: needs {sp_:.2f}x, below the {SLOW_FLOOR}x floor")
                ch += (f",setpts=PTS/{sp_:.4f},{h['crop']},"
                       f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,fps={FPS}")
            else:
                ch += f",{h['crop']},fps={FPS}"
            ch += ",scale=1080:960:flags=lanczos,setsar=1"
            if delay > 0:
                ch += f",tpad=start_mode=clone:start_duration={delay:.3f}"
            parts.append(ch + f",trim=duration={d:.3f},setpts=PTS-STARTPTS[h{k}]")
        fc = ";".join(parts) + ";[h0][h1]vstack=inputs=2[v]"
        run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc, "-map", "[v]",
             "-c:v", "libx264", "-crf", "12", "-preset", "medium", "-pix_fmt", "yuv420p", out])
        return {"src": str(out), "start": 0.4, "crop": "null", "push": 0, "tail": 0.0}

    def background(self):
        segs = []
        for i, s in enumerate(self.e["segments"]):
            base = {"t0": s["t0"], "t1": s["t1"], "xf": s.get("xf", XF)}
            if "split" in s:
                base.update(self._split(s, i))
            else:
                base.update(src=str(self.p(s["src"])), start=float(s.get("start", 0.0)),
                            crop=s.get("crop", VEO_720_CROP), push=s.get("push", 0.05),
                            # a Veo clip's last tenth of a second is not trusted; our own
                            # renders (crop "null") are used to their last frame
                            tail=s.get("tail", 0.0 if s.get("crop") == "null" else 0.1))
            base["hold"] = bool(s.get("hold"))
            segs.append(base)
        for a, b in zip(segs, segs[1:]):
            assert abs(a["t1"] - b["t0"]) < 1e-6, (a, b)
        assert abs(segs[-1]["t1"] - self.dur) < 0.02 and segs[0]["t0"] == 0, "segments must cover the clip"
        ins, chains = [], []
        for i, s in enumerate(segs):
            d = s["t1"] - s["t0"]
            xf = s["xf"] if i else 0.0
            head = min(xf, s["start"])
            pad = xf - head
            need = d + xf
            real = need - pad
            s0 = s["start"] - head
            usable = length(s["src"]) - s0 - s["tail"]
            ins += ["-i", s["src"]]
            ch = f"[{i}:v]trim=start={s0:.3f}:duration={min(real, usable):.3f},setpts=PTS-STARTPTS"
            crop = s["crop"]
            freeze = 0.0
            if usable < real - 0.02 and s.get("hold"):
                freeze = real - usable
                ch += f",{crop},fps={FPS}"
            elif usable < real - 0.02:
                speed = usable / real
                if speed < SLOW_FLOOR:
                    raise SystemExit(f"segment {i} ({Path(s['src']).name}) needs {speed:.2f}x, "
                                     f"below the {SLOW_FLOOR}x floor")
                ch += (f",setpts=PTS/{speed:.4f},{crop},"
                       f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1,fps={FPS}")
            else:
                ch += f",{crop},fps={FPS}"
            ch += ",scale=1080:1920:flags=lanczos,setsar=1"
            if crop != "null" and s["push"]:
                z = f"(1+{s['push']}*t/{real:.3f})"
                ch += (f",scale=w='trunc(1080*{z}/2)*2':h='trunc(1920*{z}/2)*2':eval=frame:flags=bicubic,"
                       "crop=1080:1920")
            if pad > 0:
                ch += f",tpad=start_mode=clone:start_duration={pad:.3f}"
            # Every segment is given a few frames MORE than its window (its last frame, held).
            # xfade ends the whole track if its first input stops even one frame before the
            # transition is over, and a window that is not a whole number of frames loses one:
            # with one-frame cuts, POL-C3-LA-02 part 1's picture stopped at 69.8 s of 137.
            ch += f",tpad=stop_mode=clone:stop_duration={freeze + 0.3:.3f}"
            chains.append(ch + f",trim=duration={need + 0.15:.3f},setpts=PTS-STARTPTS[s{i}]")
        fc = ";".join(chains)
        last = "s0"
        for i in range(1, len(segs)):
            xf = segs[i]["xf"]
            fc += (f";[{last}][s{i}]xfade=transition={self.e['segments'][i].get('transition', 'fade')}"
                   f":duration={xf}:offset={segs[i]['t0'] - xf:.3f}[x{i}]")
            last = f"x{i}"
        out = self.out / f"bg_part{self.n}.mp4"
        # an intermediate (the composite re-encodes it): fast preset, near-lossless
        run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc, "-map", f"[{last}]",
             "-c:v", "libx264", "-crf", "13", "-preset", self.e.get("bg_preset", "medium"), "-pix_fmt", "yuv420p",
             "-t", f"{self.dur}", out])
        gate_length(out, self.dur, "the background track")
        return out

    # ------------------------------------------------------------- presenter
    def _eased(self, keys):
        v0 = keys[0][1]
        expr, prev = f"{v0}", v0
        for T, v in keys[1:]:
            if abs(v - prev) < 1e-9:
                continue
            u = f"clip((t-{T - GLIDE / 2:.3f})/{GLIDE},0,1)"
            expr += f"+({v - prev:.4f})*({u}*{u}*(3-2*{u}))"
            prev = v
        return expr

    def _placement_keys(self):
        """Per scene: scale and the screen position of the crop's top-left corner.
        A hidden scene carries no placement; the move to the NEXT visible placement
        happens at its middle, where the mask is black and nobody can see it."""
        pl = self.e["place"]
        ks = []
        for i, p in enumerate(pl):
            if p.get("hidden"):
                nxt = next((q for q in pl[i + 1:] if not q.get("hidden")), None)
                if nxt:
                    ks.append(((p["t0"] + p["t1"]) / 2, nxt["s"], nxt["x0"], nxt["y0"]))
            else:
                ks.append((p["t0"], p["s"], p["x0"], p["y0"]))
        first = ks[0]
        ks[0] = (0.0, *first[1:])
        return ks

    def composite(self, captions=True, t_from=None, t_len=None, out=None):
        e = self.e
        key = json.loads(self.p(e["key"]).read_text())
        k = (f"hsvkey=hue={key['hue']}:sat={key['sat']}:val=%s:"
             f"similarity={key['sim']}:blend=0.05,format=rgba,alphaextract")
        c = e["pcrop"]
        ks = self._placement_keys()
        S = self._eased([(t, s) for t, s, _, _ in ks])
        X = self._eased([(t, x) for t, _, x, _ in ks])
        Y = self._eased([(t, y) for t, _, _, y in ks])
        smax = max(s for _, s, _, _ in ks)
        CW, CH = round(c["w"] * smax / 2) * 2 + 8, round(c["h"] * smax / 2) * 2 + 8
        L = e["layers"]
        ins = ["-i", self.out / f"bg_part{self.n}.mp4", "-i", self.p(e["heygen"]),
               "-i", self.p(L["mask"]), "-i", self.p(L["under"]), "-i", self.p(L["overlay"])]
        # A layer is sparse: `fps` holds each picture until the next.
        # The pixel format is converted BEFORE `fps`: a layer has a new picture a few times a
        # second, and converting it after `fps` converts the same picture thirty times a second.
        lay = lambda i, fmt="yuva420p": f"[{i}:v]format={fmt},fps={FPS}"
        cut_fx = e.get("cutout") or {}
        edge = int(cut_fx.get("edge", 0))
        fc = (
            # key: tools/composite.py's chain; despill gentler for this real cloth (see reel_build.py)
            f"[1:v]fps={FPS},crop={c['w']}:{c['h']}:{c['x']}:{c['y']},format=rgba,split=3[c][d1][d2];"
            f"[d1]{k % key['v1']}[a1];[d2]{k % key['v2']}[a2];"
            f"[a1][a2]blend=all_mode=darken,dilation,dilation,erosion,erosion,"
            f"eq=contrast=2.2:brightness=-0.10,erosion,erosion,gblur=sigma=1.0[al];"
            f"[c]despill=type=green:mix=0.3:expand=0,hue=s=0.9[cc];[cc][al]alphamerge,"
            # glide: rescaled every frame, padded to a fixed canvas, placed by its top-left corner
            f"scale=w='trunc({c['w']}*({S})/2)*2':h='trunc({c['h']}*({S})/2)*2':eval=frame:flags=lanczos,"
            f"pad=w={CW}:h={CH}:x=0:y=0:color=0x00000000:eval=frame[pr];"
            f"color=c=black@0.0:s=1080x1920:r={FPS},format=rgba[blank];"
            f"[blank][pr]overlay=x='{X}':y='{Y}':eval=frame:shortest=1,format=rgba,split=2[pc][pc2];"
            # the mask decides where he shows: full frame, a circle, or nowhere
            f"[pc2]alphaextract[pa];{lay(2, 'gray')}[mk];"
            f"[pa][mk]blend=all_mode=multiply:shortest=1[pm];[pc][pm]alphamerge[him0];"
            f"{lay(3)}[un];{lay(4)}[ov];"
            f"[0:v][un]overlay=0:0:eof_action=pass[b1];")
        n = 5
        if e.get("grain") and self.p(e["grain"]).exists():
            ins += ["-loop", "1", "-framerate", str(FPS), "-i", self.p(e["grain"])]
            fc += f"[b1][{n}:v]overlay=0:0:shortest=1[b1g];"
            base = "b1g"
            n += 1
        else:
            base = "b1"
        if edge:
            # the paper edge is his own matte, grown by a blur and a hard threshold; the shadow is
            # the same matte, blurred wide and dropped a little down-right
            fc += (f"[him0]split=3[him][e0][s0];"
                   f"[e0]alphaextract,gblur=sigma={edge * 0.75:.2f},lut=y='clip((val-18)*9,0,255)',gblur=sigma=0.8[ea];"
                   f"color=c=0xfbf8f0:s=1080x1920:r={FPS},format=rgba[ew];[ew][ea]alphamerge[edgeL];")
            if cut_fx.get("shadow", True):
                # a soft shadow has no detail: blurred at quarter size, a sixteenth of the work
                fc += (f"[s0]alphaextract,scale=270:480:flags=bilinear,gblur=sigma=3.5,"
                       f"scale=1080:1920:flags=bilinear,lut=y='val*0.42'[sa];"
                       f"color=c=0x1b1a17:s=1080x1920:r={FPS},format=rgba[sk];[sk][sa]alphamerge[shadowL];"
                       f"[{base}][shadowL]overlay=10:16:shortest=1[b1s];[b1s][edgeL]overlay=0:0:shortest=1[b1e];")
            else:
                fc += f"[s0]nullsink;[{base}][edgeL]overlay=0:0:shortest=1[b1e];"
            base = "b1e"
        else:
            fc += "[him0]null[him];"
        fc += f"[{base}][him]overlay=0:0:eof_action=pass[b2];[b2][ov]overlay=0:0:eof_action=pass[g]"
        if captions and L.get("captions"):
            ins += ["-i", self.p(L["captions"])]
            fc += f";{lay(n)}[cp];[g][cp]overlay=0:0:eof_action=pass[out]"
            n += 1
        else:
            fc += ";[g]null[out]"
        amap = "1:a"
        if e.get("audio") and self.p(e["audio"]).exists():
            ins += ["-i", self.p(e["audio"])]
            amap = f"{n}:a"
        audio_in = n if amap != "1:a" else None
        out = out or self.out / f"part{self.n}{'' if captions else '_no_captions'}.mp4"
        cut = []
        if t_from is not None:
            # A test window is cut on the OUTPUT side: everything before it is drawn and thrown
            # away. Slower than seeking the inputs, but an input seek drops the layer picture that
            # is on screen at t_from (it was written seconds earlier), and trimming the layers
            # inside the graph deadlocks ffmpeg's scheduler (seen 2026-10-08, ffmpeg 9.0.1).
            cut = ["-ss", f"{t_from}", "-t", f"{t_len}"]
        run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", fc,
             "-map", "[out]", "-map", amap, "-c:v", "libx264", "-crf", "17", "-preset", "medium",
             "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
             *(cut or ["-t", f"{self.dur}"]), "-threads", "4", out])
        gate_length(out, t_len if t_from is not None else self.dur, "the composite")
        return out

    def stills(self, video, times, sheet):
        from PIL import Image, ImageDraw
        tiles = []
        for t in times:
            f = self.out / "tmp" / f"still_{t:.2f}.png"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t}", "-i", str(video), "-frames:v", "1",
                            "-vf", "scale=270:480", str(f)], check=True)
            tiles.append((t, Image.open(f).convert("RGB")))
            f.unlink()
        cols = 8
        rows = (len(tiles) + cols - 1) // cols
        im = Image.new("RGB", (cols * 276, rows * 500), (18, 18, 18))
        d = ImageDraw.Draw(im)
        for i, (t, tile) in enumerate(tiles):
            x, y = (i % cols) * 276, (i // cols) * 500
            im.paste(tile, (x, y))
            d.text((x + 4, y + 484), f"{t:.2f}s", fill=(255, 220, 90))
        im.save(sheet)
        return sheet


if __name__ == "__main__":
    part = Part(sys.argv[1])
    step = sys.argv[2] if len(sys.argv) > 2 else "all"
    caps = "--no-captions" not in sys.argv
    if step in ("bg", "all"):
        part.background()
    if step in ("comp", "all"):
        part.composite(captions=caps)
    if step == "test":                  # build_part.py <edit> test <from> <seconds> -> out/test_p<N>.mp4
        a, d = float(sys.argv[3]), float(sys.argv[4])
        part.composite(captions=caps, t_from=a, t_len=d, out=part.out / f"test_p{part.n}.mp4")
    if step == "sheet":                 # one frame from the middle of every placement and 0.3 s after each cut
        video = part.out / f"part{part.n}.mp4"
        ts = sorted({round(t, 2) for p in part.e["place"] for t in ((p["t0"] + p["t1"]) / 2, min(p["t0"] + 0.3, p["t1"]))})
        print(part.stills(video, ts, part.out / f"part{part.n}_sheet.png"))
