"""Lay the caption plates over the keyed video and mux the take's own audio.

The plates are pre-rendered PNGs because Devanagari has to be SHAPED, and the
only things here that shape it correctly are Pillow-with-raqm and Chromium —
ffmpeg's drawtext is not even built in this install.

Overlay with `enable=between(...)`, never a per-pixel expression: the house note
on composite performance measured `blend=all_expr` at 17x the cost of an
enabled overlay for the same result.
"""
import json, subprocess, pathlib

W = pathlib.Path("/tmp/phy_build")
P = pathlib.Path("projects/phy-c1-sa-01")
caps = json.loads((P / "work" / "captions.json").read_text())
CARD_END = 8.50
before = len(caps)
caps = [c for c in caps if c["start"] >= CARD_END - 0.05]
print(f"  {before - len(caps)} caption(s) dropped: the card owns the screen until "
      f"{CARD_END}s and its own heading sits in the caption band")
# the plate image is centred on the house caption band (rows 62..243)
Y = (62 + 243) // 2 - 211 // 2

args = ["ffmpeg", "-v", "error", "-i", str(W / "keyed.mp4")]
for c in caps:
    args += ["-i", c["file"]]
chain, prev = [], "[0:v]"
for i, c in enumerate(caps, start=1):
    lab = f"[v{i}]"
    chain.append(f"{prev}[{i}:v]overlay=x=0:y={Y}:"
                 f"enable='between(t,{c['start']:.3f},{c['end']:.3f})'{lab}")
    prev = lab
args += ["-filter_complex", ";".join(chain),
         "-i", "inbox/phy-c1-sa-01/heygen_full.mp4",
         "-map", prev, "-map", f"{len(caps)+1}:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-shortest", "-movflags", "+faststart",
         str(P / "final" / "phy_c1_sa_01.mp4"), "-y"]
subprocess.run(args, check=True)
out = P / "final" / "phy_c1_sa_01.mp4"
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", str(out)], capture_output=True, text=True).stdout.strip()
print(f"  -> {out}  {d}s   ({len(caps)} caption plates)")
