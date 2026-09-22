"""Transitions and sound effects for HIS-C2-SA-06.

Two rules this obeys, both learned the hard way on this video:

TRANSITIONS DO NOT CHANGE DURATION. A cross dissolve or an xfade consumes time
from both sides, which would shift every later segment and undo the audio
alignment that took a rebuild to get right. So a transition here is a dip
through dark: the outgoing segment fades out over its own last frames and the
incoming one fades up over its own first frames. Frame count unchanged, audio
untouched, sync preserved by construction.

SOUND SITS UNDER THE VOICE. Cues are mixed onto the finished narration at
-12dB or lower; they punctuate, they never compete. Effects are keyed to the
PICTURE — a point pops when the label lands, a whoosh rides the camera move —
never to a caption. (See the house note: sound comes from beats, not captions.)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

W = Path("/tmp/his_build")
SFX = Path("assets/sfx")
DIP = 0.20          # seconds of fade on each side of a dip transition


def run(args):
    subprocess.run(args, check=True)


def probe(path, stream="v"):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", f"{stream}:0",
         "-count_frames", "-show_entries", "stream=nb_read_frames",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return int("".join(c for c in out if c.isdigit()))


def dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return float(out.strip())


def dip_video(src, out, *, fade_in, fade_out, tail_black=0.0):
    """Fade a segment's own first/last frames. Duration is unchanged."""
    d = dur(src)
    vf = []
    if fade_in:
        vf.append(f"fade=t=in:st=0:d={DIP}")
    if fade_out:
        vf.append(f"fade=t=out:st={d - DIP:.3f}:d={DIP}")
    if not vf:
        vf.append("null")
    run(["ffmpeg", "-v", "error", "-i", str(src), "-vf", ",".join(vf),
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-r", "30", str(out), "-y"])


def mix_cues(narration, cues, out, total):
    """Lay the cues over the narration. One ffmpeg call, amix at the end."""
    if not cues:
        run(["ffmpeg", "-v", "error", "-i", str(narration), "-c", "copy", str(out), "-y"])
        return
    args = ["ffmpeg", "-v", "error", "-i", str(narration)]
    for c in cues:
        args += ["-i", str(SFX / f"{c['name']}.wav")]
    parts, labels = [], ["[0:a]"]
    for i, c in enumerate(cues, start=1):
        ms = int(c["time"] * 1000)
        parts.append(f"[{i}:a]adelay={ms}|{ms},volume={c.get('gain',-12.0)}dB[c{i}]")
        labels.append(f"[c{i}]")
    parts.append("".join(labels) + f"amix=inputs={len(labels)}:duration=first:"
                 f"normalize=0,alimiter=limit=0.97[a]")
    args += ["-filter_complex", ";".join(parts), "-map", "[a]",
             "-t", f"{total:.3f}", "-ac", "2", "-ar", "48000",
             "-c:a", "pcm_s16le", str(out), "-y"]
    run(args)


# --------------------------------------------------------------------------- #
# The polish pass: house transitions at the cuts, and the approved cues.
#
# HOW A TRANSITION KEEPS THE DURATION. An xfade eats D seconds from the join,
# which would pull every later segment earlier and undo the audio alignment.
# So the OUTGOING segment is extended by D from its own source before the
# xfade, and the xfade offset is the outgoing segment's ORIGINAL length. The
# incoming shot then still begins on the exact frame its audio expects, the
# total is unchanged, and the audio track is never touched:
#
#     V_k  = seg_k (L_k frames) + ext_k (D_k frames)
#     out  = V_1 xfade(D_1, offset=L_1) V_2 xfade(D_2, offset=L_1+L_2) ...
#     len  = sum(L_k)                    <- what the butt-joined audio is
#
# During the blend you see the outgoing shot's EXTRA frames — material past
# where its sound ended — which is exactly what a dissolve is supposed to show.
# --------------------------------------------------------------------------- #
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.transitions import plan_transitions, audit          # noqa: E402

ORDER = ["01","02","03","04","05","06","07","08","09","10","11","12"]

# What each cut MEANS. The vocabulary decides what it looks like.
KINDS = ["scene_change",   # 01->02  pillar to hillside, voice carrying on
         "to_card",        # 02->03  into the question card
         "from_card",      # 03->04  out of the card into daylight
         "to_map_first",   # 04->05  the map is introduced
         "from_data",      # 05->06  back off the map
         "to_map",         # 06->07
         "from_data",      # 07->08
         "to_map",         # 08->09
         "continuous",     # 09->10  one explanation, one plate: no cut effect
         "continuous",     # 10->11
         "continuous"]     # 11->12  the close already fades to black

# how to extend each segment past its own end, for the blend
VEO_SRC = {"01": ("veo1_clean.mp4", 0.47), "02": ("veo2_clean.mp4", 8.65),
           "04": ("veo3_clean.mp4", 0.63), "06": ("veo4_clean.mp4", 0.55),
           "08": ("veo5_clean.mp4", 0.77)}
VEO_CONT = {"02"}                       # seg02 was re-cut; its tail resumes at 8.65
SCREEN_SRC = {
 "03": ("projects/his-c2-sa-06/manim_code/media/videos/pyq_composed/1920p30/card_his.mp4", 14.60, "card"),
 "05": ("map_engine/output/his_c2_m1_relief.mp4", 40.45, "map"),
 "07": ("map_engine/output/his_c2_m2_relief.mp4", 55.70, "map"),
}
KEY = ("format=yuva420p,chromakey=0xA1EC32:0.14:0.10,despill=type=green:mix=0.55:expand=0,"
       "split[k1][k2];[k2]alphaextract,boxblur=1.0:1[am];[k1][am]alphamerge,"
       "scale=1815:1021,setsar=1,fps=30[fg];[0:v][fg]overlay=x=-342:y=899:format=auto[v]")
KEYCARD = ("format=yuva420p,chromakey=0xA1EC32:0.14:0.10,despill=type=green:mix=0.55:expand=0,"
           "split[k1][k2];[k2]alphaextract,boxblur=1.0:1[am];[k1][am]alphamerge,"
           "scale=1139:641,setsar=1,fps=30[fg];[0:v][fg]overlay=x=-14:y=1279:format=auto[v]")
HG = "inbox/his-c2-sa-06/heygen_full.mp4"


def build_ext(seg, L, D, src=W):
    """D seconds of continuation after segment `seg` ends, as its own file."""
    d = D / 30.0
    out = src / f"ext{seg}.mp4"
    if seg in VEO_SRC:
        clip, start = VEO_SRC[seg]
        at = start + (0 if seg in VEO_CONT else L / 30.0)
        run(["ffmpeg","-v","error","-ss",f"{at:.4f}","-t",f"{d:.4f}",
             "-i",str(src/clip),"-vf","scale=1080:1920:flags=lanczos,setsar=1,fps=30",
             "-an","-c:v","libx264","-preset","medium","-crf","18",
             "-pix_fmt","yuv420p","-r","30",str(out),"-y"])
        return out
    pic, hg0, kind = SCREEN_SRC[seg]
    filt = KEYCARD if kind == "card" else KEY
    if kind == "card":                      # the card render is longer than we used
        run(["ffmpeg","-v","error","-ss",f"{L/30.0:.4f}","-t",f"{d:.4f}","-i",pic,
             "-ss",f"{hg0 + L/30.0:.4f}","-t",f"{d:.4f}","-i",HG,
             "-filter_complex",f"[1:v]{filt}","-map","[v]","-an",
             "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
             "-r","30",str(out),"-y"])
        return out
    # a map render is exactly as long as its block, so hold its last frame and
    # let the presenter keep moving over it
    still = src / f"last{seg}.png"
    run(["ffmpeg","-v","error","-sseof","-0.05","-i",pic,"-frames:v","1",str(still),"-y"])
    run(["ffmpeg","-v","error","-loop","1","-t",f"{d:.4f}","-i",str(still),
         "-ss",f"{hg0 + L/30.0:.4f}","-t",f"{d:.4f}","-i",HG,
         "-filter_complex",f"[1:v]{filt}","-map","[v]","-an",
         "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
         "-r","30",str(out),"-y"])
    return out


def polish(src=W, out=Path("projects/his-c2-sa-06/final/his_c2_sa_06.mp4")):
    L = {s: probe(src / f"seg{s}.mp4") for s in ORDER}
    trs = plan_transitions(KINDS)
    warns = audit(trs)

    # V_k = seg_k + its extension
    parts = []
    for i, s in enumerate(ORDER):
        tr = trs[i] if i < len(trs) else None
        if tr:
            ext = build_ext(s, L[s], tr.frames, src)
            lst = src / f"v{s}.txt"
            lst.write_text(f"file '{src}/seg{s}.mp4'\nfile '{ext}'\n")
            run(["ffmpeg","-v","error","-f","concat","-safe","0","-i",str(lst),
                 "-c","copy",str(src/f"v{s}.mp4"),"-y"])
        else:
            run(["ffmpeg","-v","error","-i",str(src/f"seg{s}.mp4"),"-c","copy",
                 str(src/f"v{s}.mp4"),"-y"])
        parts.append(src / f"v{s}.mp4")

    # the xfade chain covers every segment up to the last one that has a
    # transition leading into it; the rest are plain concatenation
    last = max(i for i, t in enumerate(trs) if t) + 1
    args, graph, cum, prev = ["ffmpeg","-v","error"], [], 0, None
    for i in range(last + 1):
        args += ["-i", str(parts[i])]
    for i in range(last):
        cum += L[ORDER[i]]
        tr = trs[i]
        a = prev or "[0:v]"
        lab = f"[x{i}]"
        graph.append(f"{a}[{i+1}:v]xfade=transition={tr.xfade}:"
                     f"duration={tr.seconds}:offset={cum/30.0:.4f}{lab}")
        prev = lab
    args += ["-filter_complex", ";".join(graph), "-map", prev, "-an",
             "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
             "-r","30", str(src/"chain.mp4"), "-y"]
    run(args)

    tail = ORDER[last + 1:]
    lst = src / "final.txt"
    lst.write_text(f"file '{src}/chain.mp4'\n" +
                   "".join(f"file '{src}/seg{s}.mp4'\n" for s in tail))
    run(["ffmpeg","-v","error","-f","concat","-safe","0","-i",str(lst),
         "-c","copy","-an",str(src/"pvideo.mp4"),"-y"])
    (src/"alist2.txt").write_text("".join(f"file '{src}/seg{s}.wav'\n" for s in ORDER))
    run(["ffmpeg","-v","error","-f","concat","-safe","0","-i",str(src/"alist2.txt"),
         "-c","copy",str(src/"pnarr.wav"),"-y"])

    # cues: the transition's own sound, plus the label pops
    starts, t = {}, 0
    for s in ORDER:
        starts[s] = t / 30.0
        t += L[s]
    total = t / 30.0
    import json as _json
    reg = _json.loads(Path("assets/sfx/registry.json").read_text(encoding="utf-8"))

    def at_peak(moment, name, gain):
        """A cue's `time` is its START; the gate checks time + peak_offset.
        So to land the sound ON the moment, start it that much earlier."""
        off = float(reg.get(name, {}).get("peak_offset", 0.0))
        return {"time": max(0.0, moment - off), "name": name, "gain": gain}

    cues = []
    for i, tr in enumerate(trs):
        if not tr:
            continue
        moment = starts[ORDER[i + 1]] + tr.reads_at()
        if tr.cue:
            c = at_peak(moment, tr.cue, tr.cue_gain)
            if tr.second_cue:
                c["layer"] = f"cut{i}"
            cues.append(c)
        if tr.second_cue:
            # deliberately on top of the first: one thickened sound for one cut
            c = at_peak(moment, tr.second_cue, tr.second_gain)
            c["layer"] = f"cut{i}"
            cues.append(c)
    # Re-measured on the relief maps. Their labels are cued 0.35s BEFORE the
    # word, so they finish fading in exactly ON it — verified by tracking the
    # chip area: M2's chips complete at 0.70, 8.50 and 16.40, which are the
    # spoken times. So the pop now lands on the word, not 0.40s after it.
    for s, times in {"05": [1.75], "07": [0.70, 8.50, 16.40], "09": [0.57]}.items():
        for p in times:
            cues.append(at_peak(starts[s] + p, "pop", -10.0))
    # the close lands ON dark: measured, the picture reaches black exactly where
    # segment 12 begins, so that is where the accent belongs
    # the fade completes at 4.90 into segment 11 and the picture is black from
    # there; that arrival is what the accent marks, not the end of the segment
    cues.append(at_peak(starts["11"] + 4.90, "impact", +8.0))
    cues.sort(key=lambda c: c["time"])

    mix_cues(src/"pnarr.wav", cues, src/"pmixed.wav", total)
    run(["ffmpeg","-v","error","-i",str(src/"pvideo.mp4"),"-i",str(src/"pmixed.wav"),
         "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k",
         "-ar","48000","-ac","2","-movflags","+faststart",str(out),"-y"])
    return trs, cues, total, warns
