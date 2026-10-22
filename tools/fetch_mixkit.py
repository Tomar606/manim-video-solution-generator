"""Rebuild the Mixkit sounds and music that the public repo cannot carry.

    python tools/fetch_mixkit.py              # download + cut every missing Mixkit file
    python tools/fetch_mixkit.py --check      # list which are missing, change nothing
    python tools/fetch_mixkit.py --calibrate  # (maintainers) record how each local file was cut

WHY
---
The repo is public, and the Mixkit licence allows using the files in videos but
not redistributing them as files.  So `library/sfx/**` and `library/music/**`
entries whose `source_site` is Mixkit are .gitignored.  Their manifest entries
stay, each with the Mixkit download URL and a `rebuild` block.  This script
fetches the original from Mixkit and cuts it exactly the way the committed
pipeline expects:
  offset into the source, duration, gain, fade-in and fade-out,
  48 kHz 16-bit mono for sounds, the original mp3 for music.

The `rebuild` block is MEASURED, not guessed.  `--calibrate` cross-correlates each
local file against its downloaded original, which finds the cut's real start, and
records it, because the processing notes ("trimmed, window 0.00-0.58s of trimmed
source") depend on a trim threshold that was never written down.

Run it once after cloning, from the repo root:  .venv-tools/bin/python tools/fetch_mixkit.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SFX = ROOT / "library/sfx"
MUSIC = ROOT / "library/music"
SR = 48000
UA = {"User-Agent": "Mozilla/5.0 (arivihan video pipeline; fetch_mixkit)"}


def is_mixkit(e: dict) -> bool:
    return "mixkit" in (e.get("source_site") or "").lower()


def sfx_url(e: dict) -> str | None:
    if e.get("download_url"):
        return e["download_url"]
    m = re.search(r"-(\d+)\.wav$", e.get("original_filename") or "")      # mixkit-light-button-2580.wav
    return f"https://assets.mixkit.co/active_storage/sfx/{m.group(1)}/{m.group(1)}.wav" if m else None


def download(url: str, dest: Path) -> Path:
    if not dest.exists():
        dest.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read())
    return dest


def pcm(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def calibrate(local: Path, src: Path) -> dict:
    """Where the local cut sits in the source, and how much it was scaled."""
    a, s = pcm(local), pcm(src)
    n = len(a)
    if n > len(s):
        raise ValueError("local file longer than its source")
    # FFT cross-correlation of the local cut against the whole source
    L = 1 << int(np.ceil(np.log2(len(s) + n)))
    c = np.fft.irfft(np.fft.rfft(s, L) * np.conj(np.fft.rfft(a, L)), L)[:len(s) - n + 1]
    off = int(np.argmax(c))
    seg = s[off:off + n]
    # gain from the loud middle (the fades distort the ends)
    mid = slice(int(n * 0.1), max(int(n * 0.1) + 1, int(n * 0.85)))
    gain = float(np.dot(seg[mid], a[mid]) / max(np.dot(seg[mid], seg[mid]), 1e-12))
    corr = float(np.corrcoef(seg[mid] * gain, a[mid])[0, 1]) if n > 20 else 1.0
    return {"offset_s": round(off / SR, 5), "duration_s": round(n / SR, 5), "gain": round(gain, 6),
            "fade_in_s": 0.002, "fade_out_s": 0.03, "match": round(corr, 4)}


def peak_dbfs(path: Path) -> float:
    """Peak as the sound library measures it (tools/sfx_registry.measure works at 22.05 kHz)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", "22050", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return float(20 * np.log10(max(np.abs(np.frombuffer(raw, np.float32)).max(), 1e-9)))


def rebuild(src: Path, dest: Path, r: dict) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if r.get("mode") == "silenceremove_window":
        # replays the exact ffmpeg recipe a sound was cut with, for cuts correlation cannot place
        # (a 0.3 s click is too short and too similar to its neighbours to locate reliably)
        with tempfile.TemporaryDirectory() as td:
            proc, cut = Path(td) / "proc.wav", Path(td) / "cut.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                            "silenceremove=start_periods=1:start_threshold=-45dB,aresample=48000",
                            "-ac", "1", "-sample_fmt", "s16", str(proc)], check=True)
            d = r["duration_s"]
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{r['start_s']:.3f}", "-t", f"{d:.3f}", "-i", str(proc),
                            "-af", f"afade=t=in:d=0.002,afade=t=out:st={d - 0.03:.3f}:d=0.03",
                            "-ar", "48000", "-ac", "1", "-sample_fmt", "s16", str(cut)], check=True)
            g = r["peak_target_dbfs"] - peak_dbfs(cut)
            for _ in range(3):                                   # volume is linear, but s16 rounding nudges the peak
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(cut), "-af", f"volume={g:.3f}dB",
                                "-sample_fmt", "s16", str(dest)], check=True)
                miss = r["peak_target_dbfs"] - peak_dbfs(dest)
                if abs(miss) < 0.1:
                    break
                g += miss
        return
    d, fo = r["duration_s"], r["fade_out_s"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af",
                    f"aresample={SR},atrim=start={r['offset_s']}:duration={d},asetpts=N/SR/TB,"
                    f"volume={r['gain']},afade=t=in:d={r['fade_in_s']},afade=t=out:st={max(0.0, d - fo):.4f}:d={fo}",
                    "-ac", "1", "-ar", str(SR), "-sample_fmt", "s16", str(dest)], check=True)


def entries():
    sm = json.loads((SFX / "manifest.json").read_text())
    mm = json.loads((MUSIC / "manifest.json").read_text())
    tracks = mm if isinstance(mm, list) else mm.get("tracks", [])
    return sm, mm, [e for e in sm["sounds"] if is_mixkit(e)], [t for t in tracks if is_mixkit(t)]


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    sm, mm, sfx, music = entries()
    tmp = Path(tempfile.mkdtemp(prefix="mixkit_"))
    missing = [e for e in sfx if not (ROOT / "library" / e["file"]).exists()] + \
              [t for t in music if not (ROOT / "library" / t["file"]).exists()]
    if mode == "--check":
        print(f"{len(missing)} of {len(sfx) + len(music)} Mixkit files missing")
        for e in missing:
            print("  ", e["file"])
        return 1 if missing else 0

    if mode == "--calibrate":
        bad = 0
        for e in sfx:
            local = ROOT / "library" / e["file"]
            url = sfx_url(e)
            if not local.exists() or not url:
                print("  skip", e["id"]); continue
            src = download(url, tmp / Path(url).name)
            e["download_url"] = url
            e["rebuild"] = calibrate(local, src)
            bad += e["rebuild"]["match"] < 0.98
            print(f"  {e['id']:40s} offset {e['rebuild']['offset_s']:7.3f}s  match {e['rebuild']['match']}")
        (SFX / "manifest.json").write_text(json.dumps(sm, ensure_ascii=False, indent=1))
        for t in music:                                      # music is used as downloaded: record its size to verify
            local = ROOT / "library" / t["file"]
            if local.exists():
                src = download(t["download_url"], tmp / f"m_{t['id']}.mp3")
                t["rebuild"] = {"as_downloaded": src.read_bytes() == local.read_bytes(), "bytes": local.stat().st_size}
                print(f"  music {t['id']:30s} identical to download: {t['rebuild']['as_downloaded']}")
        (MUSIC / "manifest.json").write_text(json.dumps(mm, ensure_ascii=False, indent=1))
        print("calibrated;", bad, "sounds matched below 0.98")
        return 1 if bad else 0

    done = 0
    for e in missing:
        dest = ROOT / "library" / e["file"]
        if e in music:
            download(e["download_url"], dest); done += 1
            print("  music", e["file"]); continue
        r = e.get("rebuild")
        if not r:
            print("  ! no rebuild record for", e["id"]); continue
        src = download(sfx_url(e), tmp / Path(sfx_url(e)).name)
        rebuild(src, dest, r); done += 1
        print("  sfx  ", e["file"])
    print(f"rebuilt {done} of {len(missing)} missing Mixkit files")
    return 0 if done == len(missing) else 1


if __name__ == "__main__":
    raise SystemExit(main())
