"""The sound of one part of a reel: his narration + a bed + the effects, levelled
against his voice.

    python3 tools/reel/audio.py <slug> <part>           # build
    python3 tools/reel/audio.py <slug> <part> --check   # measure what is on disk, change nothing

This file is the PROCESS and exists once. What a video SOUNDS like lives in that
video's folder, as a palette (see "the palette" below); this file never names a
sound. Everything is synthesised with numpy -- no samples, no downloads. ffmpeg
is used to decode the narration and to cross-check loudness, and for nothing else.

Reads   work/<slug>/inputs.json          each part's clip and its duration
        work/<slug>/out/cues_p<N>.json   [{"kind": "...", "t": s, "dur": s (optional)}, ...]
                                         written by the drawing code. `t` is seconds on
                                         the part's own clock; "dur": 0 means none. Missing
                                         file: the part is built with the bed alone, and the
                                         report says so.
                                         Optional per cue: "gain_db", "pan" (-1..1), "off".
        work/<slug>/design/sound.py      the palette
Writes  work/<slug>/out/audio/p<N>.wav          narration + bed + effects, exactly the
                                                part's length, 48 kHz 16-bit stereo
        work/<slug>/out/audio/p<N>_report.json  every level measured, and per cue its
                                                level, shift, trim and margin under the voice
        and nothing else: no stems. The layers exist only in memory.

THE PALETTE is a module with three names:
    VOICES = {kind: fn(dur, rng, sr) -> mono (n,) or stereo (n, 2) float array}
             `dur` is the cue's own, or None. `rng` is seeded from the cue, so the
             same cue always makes the same sound. Any level: it is set here.
    BED    = fn(t0, dur, sr) -> stereo (n, 2), the bed for ABSOLUTE seconds
             [t0, t0+dur) on one clock through the whole video.
    LEVELS = {"bed_rel_db": dB, "sfx_rel_db": {kind: dB}, "fit": {...},
              optional: "duck_db", "bed_fade_in_s", "bed_fade_out_s", "bed_ref_part",
              "offset_s": {kind: seconds from the cue's t to the start of the sound;
                           negative starts it before t}}
A kind in a cue file that the palette does not have is warned about and skipped.

THE NARRATION IS NEVER TOUCHED. The mix is his decoded samples plus the added
layers, sample for sample; if the sum would peak too high the ADDED layers come
down, never him. The report states his gain in the mix (0.00 dB) and the
delivered-file check can compare his loudness as before.

THE BED IS A FUNCTION OF ABSOLUTE TIME. Part N's bed starts at the sum of the
earlier parts' lengths, and its gain is set once, from a fixed window of the bed
against PART 1's narration. So parts 2 and 3 pick the bed up at the sample part 1
left it, at the same level. It is ducked a little while he speaks; gaps between
words are bridged so it never pumps.

LEVELS are set against the narration's integrated loudness (BS.1770, computed
here and cross-checked with ffmpeg's ebur128): the bed's integrated loudness
sits `bed_rel_db` under it before ducking; each effect's loudest 400 ms sits
`sfx_rel_db[kind]` under it.

NO EFFECT IS ALLOWED TO SIT ON A WORD. Each cue is measured against the voice in
1-4 kHz where it lands (see "the 1-4 kHz masking check"), twice: on its own, where
it must sit `fit.target_margin_db` under the syllable, and together with the bed
and whatever effects are already sounding there, where the SUM must sit
`fit.sum_margin_db` under it (default: the target less 1.5 dB; two sounds that
each just clear would add up to the target less 3). One that does not is slid a few
hundredths LATER (never earlier: a sound before its picture reads as a mistake),
up to `fit.max_shift_s[kind]`; if it still does not clear it is turned down, by
at most `fit.max_trim_db`; and one that would STILL be louder than the voice is
dropped. What was chosen for every cue is in
the report. Nobody can listen on the build machine, so those numbers are the review.

Deterministic: fixed seeds, no clocks in the output. A rebuild is byte-identical.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import wave
import zlib
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
FFMPEG = "/opt/homebrew/bin/ffmpeg"
SR = 48000
SEED = 20261007
CEILING_DB = -1.0            # true peak of the mix must stay under this
BED_REF_S = 48.0             # the bed's gain is calibrated on absolute 0..48 s, once
STEP_S = 20.0                # the bed is asked for 20 s at a time

DEFAULT_FIT = {"target_margin_db": 6.0, "max_trim_db": 8.0, "max_shift_s": {}}
DEFAULT_SFX_DB = -26.0


# ----------------------------------------------------------------- io ------
def decode(path: Path) -> np.ndarray:
    raw = subprocess.run([FFMPEG, "-v", "error", "-i", str(path), "-vn", "-ac", "2",
                          "-ar", str(SR), "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def fit(x: np.ndarray, n: int) -> np.ndarray:
    if len(x) >= n:
        return x[:n]
    return np.vstack([x, np.zeros((n - len(x), x.shape[1]), dtype=x.dtype)])


def to_pcm16(x: np.ndarray) -> np.ndarray:
    """The same rounding ffmpeg does (x * 2^15, round, clip), no dither."""
    return np.clip(np.rint(x.astype(np.float64) * 32768.0), -32768, 32767).astype("<i2")


def write_wav16(path: Path, pcm: np.ndarray) -> None:
    """Canonical 44-byte header + samples, written beside the target and renamed
    into place, so a reader never sees half a file."""
    tmp = path.with_name(path.name + ".part")
    try:
        with wave.open(str(tmp), "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def read_wav16(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        if (w.getnchannels(), w.getsampwidth(), w.getframerate()) != (2, 2, SR):
            sys.exit(f"{path}: expected 48 kHz 16-bit stereo, found {w.getnchannels()} ch "
                     f"{8 * w.getsampwidth()}-bit {w.getframerate()} Hz")
        raw = w.readframes(w.getnframes())
    return np.frombuffer(raw, dtype="<i2").reshape(-1, 2)


def ffmpeg_ebur128(path: Path) -> dict:
    err = subprocess.run([FFMPEG, "-hide_banner", "-nostats", "-i", str(path), "-vn",
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    summ = err[err.rfind("Summary:"):]
    try:
        return {"I": float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1)),
                "TP": float(re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", summ).group(1))}
    except AttributeError:
        return {"I": None, "TP": None}


def fast_len(n: int) -> int:
    """Smallest 2^a 3^b 5^c >= n, so an FFT never hits a slow size."""
    best = None
    p5 = 1
    while p5 < 2 * n:
        p35 = p5
        while p35 < 2 * n:
            m = p35
            while m < n:
                m *= 2
            best = m if best is None or m < best else best
            p35 *= 3
        p5 *= 5
    return best


def db(x: float) -> float:
    return float(20 * np.log10(max(x, 1e-12)))


def _rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(x, dtype=np.float64)))) if len(x) else 0.0


def pan(mono: np.ndarray, p: float) -> np.ndarray:
    """p in [-1, 1], constant power."""
    a = (float(np.clip(p, -1, 1)) + 1) * np.pi / 4
    return np.stack([mono * np.cos(a), mono * np.sin(a)], axis=1)


# ------------------------------------------------------- BS.1770 loudness ---
def _kweight_response(n: int) -> np.ndarray:
    w = 2 * np.pi * np.fft.rfftfreq(n, 1 / SR) / SR
    z = np.exp(-1j * w)

    def biq(b, a):
        return (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)
    return (biq([1.53512485958697, -2.69169618940638, 1.19839281085285],
                [1.0, -1.69065929318241, 0.73248077421585]) *
            biq([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621]))


_KW: dict = {}


def _blocks(x: np.ndarray, win: float, hop: float, lead: int = 0, tail: int = 0) -> np.ndarray:
    """Mean-square loudness (LUFS) of each window, summed over channels. `lead`
    and `tail` are samples of silence imagined around x. One channel and one
    chunk at a time, so a whole part never needs more than a couple of mono
    float64 arrays. A short signal gets a short FFT (sizes come in octaves, so
    only a handful of filter responses are ever cached)."""
    W, H = int(win * SR), int(hop * SR)
    m = max(lead + len(x) + tail, W)
    C = SR // 4
    while C < m and C < 10 * SR:
        C *= 2
    P = 16384                         # a pre-roll longer than the filter's memory
    n = fast_len(C + P + 4096)
    if n not in _KW:
        _KW[n] = _kweight_response(n)
    starts = np.arange(0, m - W + 1, H)
    ms = np.zeros(len(starts))
    for ch in range(x.shape[1]):
        e = np.zeros(m + 1)
        acc = 0.0
        for a in range(0, m, C):
            b = min(a + C, m)
            buf = np.zeros(C + P)
            lo, hi = max(a - P, lead), min(b, lead + len(x))      # the part of x inside [a-P, b)
            if hi > lo:
                buf[lo - (a - P): hi - (a - P)] = x[lo - lead: hi - lead, ch]
            y = np.fft.irfft(np.fft.rfft(buf, n=n) * _KW[n], n=n)[P:P + (b - a)]
            e[a + 1:b + 1] = acc + np.cumsum(y * y)
            acc = e[b]
        ms += (e[starts + W] - e[starts]) / W
    return -0.691 + 10 * np.log10(np.maximum(ms, 1e-20))


def integrated(x: np.ndarray) -> float:
    lb = _blocks(x, 0.4, 0.1)
    lb = lb[lb > -70]
    if not len(lb):
        return -120.0
    rel = 10 * np.log10(np.mean(10 ** (lb / 10))) - 10
    lb = lb[lb > rel]
    return float(10 * np.log10(np.mean(10 ** (lb / 10))))


def momentary_max(x: np.ndarray) -> float:
    k = int(0.4 * SR)
    return float(_blocks(x, 0.4, 0.01, lead=k, tail=k).max())


def true_peak(x: np.ndarray, over: int = 8) -> float:
    """Inter-sample peak in dBFS. Only the neighbourhoods of the loudest samples
    are oversampled (anything 4 dB under the sample peak cannot overtake it in
    programme material), 128 samples at a time with 192 of context each side."""
    pk = float(np.abs(x).max()) if len(x) else 0.0
    if pk <= 0:
        return -120.0
    B, CTX = 128, 192
    L = B + 2 * CTX
    taper = np.ones(L)
    taper[:64] = 0.5 - 0.5 * np.cos(np.pi * np.arange(64) / 64)
    taper[-64:] = taper[:64][::-1]
    best = pk
    for ch in range(x.shape[1]):
        v = x[:, ch]
        blocks = np.unique(np.flatnonzero(np.abs(v) >= pk * 0.63) // B)
        vp = np.concatenate([np.zeros(CTX, v.dtype), v, np.zeros(CTX + B, v.dtype)])
        for i in range(0, len(blocks), 256):
            idx = blocks[i:i + 256, None] * B + np.arange(L)[None, :]
            S = np.fft.rfft(vp[idx].astype(np.float64) * taper, axis=1)
            S[:, -1] *= 0.5
            Y = np.zeros((len(idx), L * over // 2 + 1), dtype=complex)
            Y[:, :S.shape[1]] = S
            y = np.fft.irfft(Y, n=L * over, axis=1) * over
            best = max(best, float(np.abs(y[:, CTX * over:(CTX + B) * over]).max()))
    return db(best)


# ------------------------------------------------------ voice and ducking ---
def voice_active(narr: np.ndarray, hop_s: float = 0.01) -> tuple[np.ndarray, int]:
    hop = int(hop_s * SR)
    m = narr.mean(axis=1)
    nf = len(m) // hop
    lvl = 10 * np.log10(np.mean(m[:nf * hop].reshape(nf, hop) ** 2, axis=1) + 1e-12)
    return lvl > np.percentile(lvl, 95) - 32, hop


def active_samples(narr: np.ndarray) -> np.ndarray:
    act, hop = voice_active(narr)
    a = np.repeat(act, hop)[:len(narr)]
    return np.concatenate([a, np.zeros(len(narr) - len(a), dtype=bool)])


def duck_gain(narr: np.ndarray, duck_db: float) -> np.ndarray:
    """Per-sample linear gain: -duck_db while he speaks, 0 dB in the gaps.
    Short gaps between words are bridged (hold) so the bed never pumps."""
    active, hop = voice_active(narr)
    nf = len(active)
    hold = 25  # 250 ms: every gap between words is bridged
    held = active.copy()
    for i in np.flatnonzero(active):
        held[i:i + hold] = True
    tgt = np.where(held, -duck_db, 0.0)
    g = np.zeros(nf)
    cur = 0.0
    a_att, a_rel = np.exp(-1 / 8.0), np.exp(-1 / 35.0)   # 80 ms down, 350 ms up
    for i in range(nf):
        a = a_att if tgt[i] < cur else a_rel
        cur = a * cur + (1 - a) * tgt[i]
        g[i] = cur
    out = np.empty(len(narr), dtype=np.float32)
    xp = np.arange(nf) * hop + hop / 2
    for a in range(0, len(narr), 20 * SR):
        b = min(a + 20 * SR, len(narr))
        out[a:b] = 10 ** (np.interp(np.arange(a, b), xp, g) / 20)
    return out


# ------------------------------------------------- the 1-4 kHz masking check
# "Does an effect sit above the voice in 1-4 kHz at the same moment?" Speech
# drops 30-40 dB inside that band for 20-50 ms between syllables (closures,
# nasals), so a frame-by-frame comparison flags every audible sound ever made.
# The comparison that means something is at the syllable: 1-4 kHz power over a
# 200 ms window, voice against effect, on every frame that lies inside a word
# (broadband voice activity; the pauses between words have nothing to mask).
# The 50 ms frame-by-frame count is reported beside it for transparency.
BAND = (1000.0, 4000.0)
FRAME, HOP = 2400, 600            # 50 ms frames, 12.5 ms hop
SMOOTH = 13                       # 13 frames = a 200 ms window


def band_pow(x: np.ndarray, lo: float = BAND[0], hi: float = BAND[1]) -> np.ndarray:
    """Linear power of x inside lo..hi Hz per 50 ms frame; stereo is averaged.
    Frame k covers samples [k*HOP, k*HOP + FRAME)."""
    if x.ndim == 1:
        x = x[:, None]
    if len(x) < FRAME:
        x = np.vstack([x, np.zeros((FRAME - len(x), x.shape[1]), dtype=x.dtype)])
    nfr = 1 + (len(x) - FRAME) // HOP
    f = np.fft.rfftfreq(FRAME, 1 / SR)
    sel = (f >= lo) & (f < hi)
    win = np.hanning(FRAME).astype(np.float32)
    p = np.zeros(nfr)
    for k0 in range(0, nfr, 1024):                    # chunks: small temporaries
        idx = np.arange(FRAME)[None, :] + HOP * np.arange(k0, min(k0 + 1024, nfr))[:, None]
        for ch in range(x.shape[1]):
            X = np.fft.rfft(x[:, ch][idx] * win, axis=1)[:, sel]
            p[k0:k0 + len(idx)] += (X.real ** 2 + X.imag ** 2).sum(axis=1)
    return p / (x.shape[1] * float((win ** 2).sum()) * FRAME / 2)


def smooth(p: np.ndarray) -> np.ndarray:
    return np.convolve(p, np.ones(SMOOTH) / SMOOTH, mode="same")


class Voice:
    """The narration's 1-4 kHz envelope, computed once per part."""

    def __init__(self, narr: np.ndarray):
        self.fine = band_pow(narr)
        self.slow = smooth(self.fine)
        act, hop = voice_active(narr)                 # 10 ms frames, broadband: is he inside a word
        c = np.concatenate([[0], np.cumsum(np.repeat(act, hop))])
        a = np.minimum(np.arange(len(self.fine)) * HOP, len(c) - 1)
        b = np.minimum(a + FRAME, len(c) - 1)
        self.speaking = (c[b] - c[a]) >= FRAME // 2
        d = 10 * np.log10(self.slow + 1e-14)
        self.floor = 10 ** ((np.percentile(d, 95) - 30) / 10)    # below this: nothing to mask
        self.p95_db = float(np.percentile(d, 95))

    def against(self, o_fine: np.ndarray, k0: int = 0) -> dict:
        """o_fine: band power of the added sound on the same frame grid, from frame k0.
        margin_db is None when no word lies under the sound."""
        k = min(len(self.fine) - k0, len(o_fine))
        if k <= 0:
            return {"frames_on_voice": 0, "margin_db": None, "frames_above_voice": 0,
                    "frames_within_6db": 0, "energy_margin_db": None, "above_voice_50ms": 0}
        o_f, o_s = o_fine[:k], smooth(o_fine)[:k]
        v_f, v_s = self.fine[k0:k0 + k], self.slow[k0:k0 + k]
        sp = self.speaking[k0:k0 + k]
        both = sp & (v_s > self.floor) & (o_s > 1e-9)             # inside a word, and the sound sounding
        if not both.any():
            return {"frames_on_voice": 0, "margin_db": None, "frames_above_voice": 0,
                    "frames_within_6db": 0, "energy_margin_db": None, "above_voice_50ms": 0}
        mg = 10 * np.log10(v_s[both] / o_s[both])
        fine = sp & (v_f > self.floor) & (o_f > 1e-9)
        return {"frames_on_voice": int(both.sum()), "margin_db": round(float(mg.min()), 1),
                "frames_above_voice": int((mg < 0).sum()), "frames_within_6db": int((mg < 6).sum()),
                "energy_margin_db": round(float(10 * np.log10(v_s[both].sum() / o_s[both].sum())), 1),
                "above_voice_50ms": int((o_f[fine] > v_f[fine]).sum())}

    def against_cue(self, y: np.ndarray, st: int, under: tuple = ()) -> dict:
        """One effect (y, starting at sample st) against the voice around it.
        `under` is what is already sounding there -- the bed, and the effects
        placed so far. It counts against the voice too: the SUM has to clear."""
        k0 = max(0, st // HOP - SMOOTH - 4)
        a = k0 * HOP
        b = st + len(y) + (SMOOTH + 4) * HOP + FRAME
        buf = np.zeros((b - a, 2), dtype=np.float32)
        for u in under:
            seg = u[a:min(b, len(u))]
            buf[:len(seg)] += seg
        buf[st - a: st - a + len(y)] += y
        return self.against(band_pow(buf), k0)


# ------------------------------------------------------------- the inputs ---
class Job:
    def __init__(self, slug: str, part: int, cues: str | None, out: str | None):
        self.slug, self.part = slug, part
        self.work = ROOT / "work" / slug
        man = self.work / "inputs.json"
        if not man.exists():
            sys.exit(f"{man} does not exist. Run tools/ingest.py first.")
        parts = {int(p["part"]): p for p in json.loads(man.read_text(encoding="utf-8"))["parts"]}
        if part not in parts:
            sys.exit(f"{man} has no part {part} (it has {sorted(parts)})")
        self.clips = {k: ROOT / p["clip"]["path"] for k, p in parts.items()}
        self.samples = {k: int(round(float(p["clip"]["duration"]) * SR)) for k, p in parts.items()}
        self.n = self.samples[part]
        self.n0 = sum(self.samples[k] for k in sorted(parts) if k < part)   # where this part starts on the bed's clock
        self.narration = self.clips[part]
        if not self.narration.exists():
            sys.exit(f"{self.narration} does not exist")
        self.cues_path = Path(cues) if cues else self.work / "out" / f"cues_p{part}.json"
        self.out = Path(out) if out else self.work / "out" / "audio"
        self.wav = self.out / f"p{part}.wav"
        self.report = self.out / f"p{part}_report.json"
        self.palette_path = self.work / "design" / "sound.py"

    def rel(self, p: Path) -> str:
        try:
            return str(p.resolve().relative_to(ROOT))
        except ValueError:
            return str(p)

    def palette(self):
        if not self.palette_path.exists():
            sys.exit(f"{self.palette_path} does not exist: this video has no sound palette yet.")
        sys.dont_write_bytecode = True                 # never leave a __pycache__ in a design folder
        spec = importlib.util.spec_from_file_location(f"sound_{self.slug.replace('-', '_')}", self.palette_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in ("VOICES", "BED", "LEVELS"):
            if not hasattr(mod, name):
                sys.exit(f"{self.palette_path} must define {name}")
        return mod

    def cues(self) -> tuple[list | None, list]:
        """(cues, problems). cues is None when the file does not exist."""
        if not self.cues_path.exists():
            return None, []
        try:
            raw = json.loads(self.cues_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"{self.cues_path} is not valid JSON ({e}). Nothing was written.")
        if isinstance(raw, dict):
            raw = raw.get("cues", [])
        good, bad = [], []
        for i, c in enumerate(raw if isinstance(raw, list) else []):
            kind = c.get("kind", c.get("name")) if isinstance(c, dict) else None
            t = c.get("t") if isinstance(c, dict) else None
            dur = c.get("dur") if isinstance(c, dict) else None
            if not isinstance(kind, str) or isinstance(t, bool) or not isinstance(t, (int, float)) \
                    or not np.isfinite(t):
                bad.append({"index": i, "cue": c, "why": "needs a string 'kind' and a number 't'"})
            elif dur is not None and (isinstance(dur, bool) or not isinstance(dur, (int, float))
                                      or not np.isfinite(dur) or dur < 0):
                bad.append({"index": i, "cue": c, "why": "'dur' must be a number, 0 or more"})
            elif c.get("off"):
                bad.append({"index": i, "cue": c, "why": "off"})
            else:
                good.append(dict(c, kind=kind, t=float(t), dur=float(dur) if dur else None, index=i))   # 0 = none
        good.sort(key=lambda c: (c["t"], c["index"]))
        return good, bad


# --------------------------------------------------------------- the bed ----
def as_stereo(x, n: int | None = None, p: float = 0.0, what: str = "sound") -> np.ndarray:
    x = np.asarray(x)
    if x.ndim == 1:
        x = pan(x.astype(np.float64), p)
    elif x.ndim == 2 and x.shape[1] == 2:
        x = x.astype(np.float64)
        if p:
            x = x * np.array([min(1.0, 1 - p), min(1.0, 1 + p)])
    else:
        raise ValueError(f"{what}: expected a mono (n,) or stereo (n, 2) array, got shape {x.shape}")
    if not np.all(np.isfinite(x)):
        raise ValueError(f"{what}: not finite")
    if n is not None and len(x) != n:
        if abs(len(x) - n) > 2:
            raise ValueError(f"{what}: asked for {n} samples, got {len(x)}")
        x = fit(x, n)
    return x


def render_bed(pal, n0: int, n: int) -> np.ndarray:
    """Absolute samples [n0, n0+n), a piece at a time."""
    out = np.empty((n, 2), dtype=np.float32)
    step = int(STEP_S * SR)
    for a in range(0, n, step):
        m = min(step, n - a)
        out[a:a + m] = as_stereo(pal.BED((n0 + a) / SR, m / SR, SR), m, what="BED")
    return out


# ------------------------------------------------------------- the build ----
def build(job: Job) -> dict:
    pal = job.palette()
    lv = pal.LEVELS
    part, n = job.part, job.n
    narr = fit(decode(job.narration), n)
    L_n = integrated(narr)
    ref_part = int(lv.get("bed_ref_part", 1))
    if ref_part == part or ref_part not in job.clips:
        ref_part, L_ref = part, L_n
    else:
        L_ref = integrated(decode(job.clips[ref_part]))
    print(f"narration p{part}: {L_n:.2f} LUFS integrated (bed reference p{ref_part}: {L_ref:.2f})")

    # bed ---------------------------------------------------------------
    bed_rel = float(lv.get("bed_rel_db", -27.0))
    duck_db = float(lv.get("duck_db", 3.0))
    cal = integrated(render_bed(pal, 0, int(BED_REF_S * SR)))
    bed = render_bed(pal, job.n0, n)
    bed *= np.float32(10 ** ((L_ref + bed_rel - cal) / 20))
    dg = duck_gain(narr, duck_db)
    bed *= dg[:, None]
    dgd = 20 * np.log10(dg)
    duck = {"duck_db": duck_db, "mean_db": round(float(dgd.mean()), 2),
            "time_ducked": round(float((dgd < -duck_db / 2).mean()), 3)}
    del dg, dgd
    fi = int(float(lv.get("bed_fade_in_s", 1.0) if part == 1 else min(0.4, lv.get("bed_fade_in_s", 0.4))) * SR)
    fo = int(float(lv.get("bed_fade_out_s", 0.4)) * SR)
    if fi:
        bed[:fi] *= (0.5 - 0.5 * np.cos(np.pi * np.linspace(0, 1, fi)))[:, None].astype(np.float32)
    if fo:
        bed[-fo:] *= (0.5 + 0.5 * np.cos(np.pi * np.linspace(0, 1, fo)))[:, None].astype(np.float32)

    # effects -----------------------------------------------------------
    voice = Voice(narr)
    cues, problems = job.cues()
    bed_only = cues is None
    skipped = [{"index": b["index"], "cue": b["cue"], "why": b["why"]} for b in problems]
    for b in problems:
        if b["why"] != "off":
            print(f"  WARNING: cue {b['index']} skipped ({b['why']}): {json.dumps(b['cue'], ensure_ascii=False)}")
    if bed_only:
        print(f"  {job.rel(job.cues_path)} does not exist: building p{part} with the BED ONLY")
    fitcfg = dict(DEFAULT_FIT, **lv.get("fit", {}))
    target, max_trim = float(fitcfg["target_margin_db"]), float(fitcfg["max_trim_db"])
    sum_floor = float(fitcfg.get("sum_margin_db", target - 1.5))
    max_shift, offset = fitcfg.get("max_shift_s", {}), lv.get("offset_s", {})
    levels = lv.get("sfx_rel_db", {})
    sfx = np.zeros((n + 6 * SR, 2), dtype=np.float32)
    rows, seen, unknown = [], {}, {}
    for c in cues or []:
        kind, t = c["kind"], c["t"]
        if kind not in pal.VOICES:
            unknown[kind] = unknown.get(kind, 0) + 1
            skipped.append({"index": c["index"], "cue": {"kind": kind, "t": t}, "why": "unknown kind"})
            continue
        if not 0 <= t < n / SR:
            print(f"  WARNING: cue {c['index']} skipped ({kind} at {t} s is outside the part, 0..{n / SR:.2f} s)")
            skipped.append({"index": c["index"], "cue": {"kind": kind, "t": t}, "why": "outside the part"})
            continue
        key = (kind, int(round(t * 1000)))
        seen[key] = seen.get(key, -1) + 1
        rng = np.random.default_rng([SEED, part, zlib.crc32(kind.encode()), key[1], seen[key]])
        try:
            y = as_stereo(pal.VOICES[kind](c["dur"], rng, SR), p=float(c.get("pan", 0.0)), what=kind)
        except Exception as e:                        # one bad voice must not cost the part
            print(f"  WARNING: cue {c['index']} skipped ({kind} at {t} s failed: {e})")
            skipped.append({"index": c["index"], "cue": {"kind": kind, "t": t}, "why": f"failed: {e}"})
            continue
        if len(y) > 5 * SR + int((c["dur"] or 0) * SR) or len(y) < 16:
            skipped.append({"index": c["index"], "cue": {"kind": kind, "t": t}, "why": f"{len(y)} samples"})
            continue
        k = min(int(0.03 * SR), len(y) // 4)          # never end on a cut
        y[-k:] *= np.linspace(1, 0, k)[:, None]
        if kind not in levels:
            print(f"  WARNING: LEVELS['sfx_rel_db'] has no '{kind}'; using {DEFAULT_SFX_DB} dB")
            levels = dict(levels, **{kind: DEFAULT_SFX_DB})
        lvl = float(levels[kind]) + float(c.get("gain_db", 0.0))
        y = (y * 10 ** ((L_n + lvl - momentary_max(y)) / 20)).astype(np.float32)
        base = int(round((t + float(offset.get(kind, 0.0))) * SR))
        if base < 0:
            y, base = y[-base:], 0

        def short(y, st):
            """How many dB this cue is short of clearing, alone and in the sum."""
            m, ms = voice.against_cue(y, st), voice.against_cue(y, st, (bed, sfx))
            need = max(target - (99.0 if m["margin_db"] is None else m["margin_db"]),
                       sum_floor - (99.0 if ms["margin_db"] is None else ms["margin_db"]))
            return need, m, ms

        best = None
        for j in range(int(float(max_shift.get(kind, 0.0)) / 0.02 + 1e-6) + 1):
            sh = round(0.02 * j, 2)
            st = base + int(round(sh * SR))
            need, m, ms = short(y, st)
            if best is None or need < best[0] - 1e-9:
                best = (need, sh, st, m, ms)
            if need <= 0:
                break
        need, sh, st, m, ms = best
        # Turn it down until it clears. What is under the cue does not move with
        # it, so one step of `need` can fall short in the sum: repeat.
        trim = 0.0
        for _ in range(6):
            if need <= 0.04 or trim >= max_trim - 1e-9:
                break
            step = min(need + 0.2, max_trim - trim)
            y = y * np.float32(10 ** (-step / 20))
            trim += step
            need, m, ms = short(y, st)
        dropped = ms["margin_db"] is not None and ms["margin_db"] < 0
        if not dropped:
            y = y[:max(0, len(sfx) - st)]             # a long sound near the end: the part's end cuts it
            sfx[st:st + len(y)] += y
        rows.append({"t": round(t, 3), "kind": kind, "dur": c["dur"], "starts_at": round(st / SR, 3),
                     "level_rel_db": round(lvl - trim, 1), "shift_s": sh, "trim_db": round(trim, 1),
                     "margin_db": m["margin_db"], "sum_margin_db": ms["margin_db"],
                     "on_a_word": m["margin_db"] is not None,
                     "energy_margin_db": m["energy_margin_db"], "frames_above_voice": ms["frames_above_voice"],
                     "peak_dbfs": round(db(float(np.abs(y).max())), 1), "dropped": bool(dropped)})
    for kind, k in sorted(unknown.items()):
        print(f"  WARNING: unknown kind '{kind}' ({k} cue{'s' if k > 1 else ''}) skipped; "
              f"the palette has {sorted(pal.VOICES)}")
    sfx = sfx[:n]
    k = int(0.03 * SR)
    sfx[-k:] *= np.linspace(1, 0, k, dtype=np.float32)[:, None]

    # mix: his samples + the added layers; only the added layers ever move
    act = active_samples(narr)
    L_bed = integrated(bed)
    bed_info = {
        "t0_s": round(job.n0 / SR, 6), "target_rel_db": bed_rel,
        "reference": f"part {ref_part} narration, {L_ref:.2f} LUFS", "calibration_lufs": round(cal, 2),
        "I_lufs": round(L_bed, 2), "rel_voice_db": round(L_bed - L_n, 2),
        "rms_dbfs_while_speaking": round(db(_rms(bed[act])), 2), "rms_dbfs_in_gaps": round(db(_rms(bed[~act])), 2),
        "sample_peak_dbfs": round(db(float(np.abs(bed).max())), 2),
        "band_1_4k_vs_voice": voice.against(band_pow(bed)), "duck": duck}
    placed = [r for r in rows if not r["dropped"]]
    on_word = [r["margin_db"] for r in placed if r["margin_db"] is not None]
    sums = [r["sum_margin_db"] for r in placed if r["sum_margin_db"] is not None]
    by_kind: dict = {}
    for r in placed:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    sfx_info = {
        "cues_in_file": None if bed_only else len(cues) + len(problems), "placed": len(placed),
        "shifted": sum(r["shift_s"] > 0 for r in placed), "turned_down": sum(r["trim_db"] > 0 for r in placed),
        "dropped_would_sit_on_a_word": sum(r["dropped"] for r in rows), "skipped": len(skipped),
        "on_a_word": len(on_word), "in_a_pause": len(placed) - len(on_word),
        "worst_margin_db": min(on_word) if on_word else None,
        "worst_sum_margin_db": min(sums) if sums else None,
        "under_target": sum(v < target - 0.05 for v in on_word), "above_voice": sum(v < 0 for v in sums),
        "target_margin_db": target, "sum_margin_db": sum_floor, "max_trim_db": max_trim,
        "by_kind": dict(sorted(by_kind.items())),
        "momentary_max_rel_voice_db": round(momentary_max(sfx) - L_n, 2) if placed else None,
        "all_together_1_4k_vs_voice": voice.against(band_pow(sfx)) if placed else None}
    del act
    bed += sfx
    del sfx
    added, pulled = bed, 0.0
    nar_tp = true_peak(narr)
    if nar_tp > CEILING_DB:
        print(f"  WARNING: the narration alone peaks at {nar_tp:.2f} dBFS true peak; it is not altered, "
              f"so the mix cannot be brought under {CEILING_DB} dBFS")
    else:
        for _ in range(80):
            if true_peak(narr + added) <= CEILING_DB - 0.1:
                break
            added *= np.float32(10 ** (-0.5 / 20))
            pulled -= 0.5
        if pulled:
            print(f"  peak too hot: bed + effects lowered {-pulled:.1f} dB (the narration is not touched)")
    pcm = to_pcm16(narr + added)
    del added
    job.out.mkdir(parents=True, exist_ok=True)
    write_wav16(job.wav, pcm)

    rep = {"slug": job.slug, "part": part,
           "built": "BED ONLY (no cue file)" if bed_only else "bed + effects",
           "narration_file": job.rel(job.narration), "cue_file": None if bed_only else job.rel(job.cues_path),
           "palette": job.rel(job.palette_path), "added_layers_pulled_db": pulled,
           "measured": measure(job, narr, pcm, voice, L_n),
           "bed": bed_info, "effects": sfx_info, "skipped": skipped}
    txt = json.dumps(rep, ensure_ascii=False, indent=1)[:-2] + ',\n "cues": [\n'
    txt += ",\n".join("  " + json.dumps(r, ensure_ascii=False) for r in rows) + "\n ]\n}\n"
    job.report.write_text(txt, encoding="utf-8")
    rep["cues"] = rows
    return rep


# --------------------------------------------------------------- measure ----
def measure(job: Job, narr: np.ndarray, pcm: np.ndarray, voice: Voice | None = None,
            L_n: float | None = None) -> dict:
    """Everything that can be measured from the file on disk and the narration
    alone. The build and --check both call this, on the 16-bit samples as written."""
    n = job.n
    voice = voice or Voice(narr)
    L_n = integrated(narr) if L_n is None else L_n
    mix = fit(pcm.astype(np.float32) / np.float32(32768.0), n)
    added = mix - narr                                   # bed + effects (+ 16-bit rounding)
    act = active_samples(narr)
    L_mix = integrated(mix)
    L_add = integrated(added)
    src, out = ffmpeg_ebur128(job.narration), ffmpeg_ebur128(job.wav)
    gain = float(np.vdot(mix.astype(np.float64), narr.astype(np.float64))
                 / max(np.vdot(narr.astype(np.float64), narr.astype(np.float64)), 1e-20))
    r = {
        "samples": int(len(pcm)), "samples_expected": n, "seconds": round(len(pcm) / SR, 6),
        "bytes": job.wav.stat().st_size, "sha256": hashlib.sha256(job.wav.read_bytes()).hexdigest(),
        "narration": {"I_lufs": round(L_n, 2), "ffmpeg_I_lufs": src["I"],
                      "true_peak_dbfs": round(true_peak(narr), 2), "ffmpeg_TP_dbfs": src["TP"]},
        "narration_gain_in_mix_db": round(db(abs(gain)), 3),
        "mix": {"I_lufs": round(L_mix, 2), "ffmpeg_I_lufs": out["I"], "I_minus_narration_db": round(L_mix - L_n, 2),
                "true_peak_dbfs": round(true_peak(mix), 2), "ffmpeg_TP_dbfs": out["TP"],
                "sample_peak_dbfs": round(db(float(np.abs(mix).max())), 2),
                "samples_at_full_scale": int((np.abs(pcm.astype(np.int32)) >= 32767).sum())},
        "added_layers": {"I_lufs": round(L_add, 2), "rel_voice_db": round(L_add - L_n, 2),
                         "rms_dbfs_while_speaking": round(db(_rms(added[act])), 2),
                         "rms_dbfs_in_gaps": round(db(_rms(added[~act])), 2),
                         "sample_peak_dbfs": round(db(float(np.abs(added).max())), 2),
                         "band_1_4k_vs_voice": voice.against(band_pow(added))},
        "voice_1_4k": {"p95_db_200ms": round(voice.p95_db, 1),
                       "speaking_floor_db": round(float(10 * np.log10(voice.floor)), 1)},
    }
    b = r["added_layers"]["band_1_4k_vs_voice"]
    r["gates"] = {
        "length_exact": r["samples"] == n,
        "no_clipping": r["mix"]["samples_at_full_scale"] == 0,
        "true_peak_under_ceiling": r["mix"]["true_peak_dbfs"] < CEILING_DB
        and (out["TP"] is None or out["TP"] <= CEILING_DB),
        "narration_untouched": abs(r["narration_gain_in_mix_db"]) < 0.05,
        "nothing_above_the_voice_1_4k": b["frames_above_voice"] == 0,
    }
    return r


def show(job: Job, rep: dict) -> bool:
    m, part = rep["measured"], job.part
    print(f"p{part}: {m['samples']} samples = {m['seconds']:.6f} s (expected {m['samples_expected']}), "
          f"{m['bytes'] / 1e6:.1f} MB, {rep.get('built', 'as found on disk')}")
    print(f"  narration  I {m['narration']['I_lufs']:.2f} LUFS (ffmpeg {m['narration']['ffmpeg_I_lufs']})  "
          f"TP {m['narration']['true_peak_dbfs']:.2f} dBFS (ffmpeg {m['narration']['ffmpeg_TP_dbfs']})  "
          f"gain in the mix {m['narration_gain_in_mix_db']:+.3f} dB")
    print(f"  mix        I {m['mix']['I_lufs']:.2f} LUFS (ffmpeg {m['mix']['ffmpeg_I_lufs']}), "
          f"{m['mix']['I_minus_narration_db']:+.2f} vs narration   TP {m['mix']['true_peak_dbfs']:.2f} dBFS "
          f"(ffmpeg {m['mix']['ffmpeg_TP_dbfs']})   {m['mix']['samples_at_full_scale']} samples at full scale")
    a = m["added_layers"]
    print(f"  added      I {a['I_lufs']:.2f} LUFS = {a['rel_voice_db']:.1f} dB vs voice; rms "
          f"{a['rms_dbfs_while_speaking']:.1f} dBFS speaking / {a['rms_dbfs_in_gaps']:.1f} in gaps; "
          f"1-4 kHz worst margin {a['band_1_4k_vs_voice']['margin_db']} dB, "
          f"{a['band_1_4k_vs_voice']['frames_above_voice']} frames above the voice")
    if "bed" in rep:
        b, e = rep["bed"], rep["effects"]
        print(f"  bed        I {b['I_lufs']:.2f} LUFS = {b['rel_voice_db']:.1f} dB vs voice as mixed "
              f"(target {b['target_rel_db']} before a {b['duck']['duck_db']} dB duck); "
              f"1-4 kHz worst margin {b['band_1_4k_vs_voice']['margin_db']} dB; from {b['t0_s']} s on the bed's clock")
        if e["cues_in_file"] is None:
            print("  effects    none: no cue file")
        else:
            print(f"  effects    {e['cues_in_file']} cues: {e['placed']} placed ({e['shifted']} shifted, "
                  f"{e['turned_down']} turned down), {e['dropped_would_sit_on_a_word']} dropped, "
                  f"{e['skipped']} skipped; {e['on_a_word']} on a word, worst margin {e['worst_margin_db']} dB "
                  f"({e['under_target']} under the {e['target_margin_db']} dB target), worst with the bed and the "
                  f"other effects under it {e['worst_sum_margin_db']} dB ({e['above_voice']} above the voice); "
                  f"{e['by_kind']}")
    bad = [k for k, v in m["gates"].items() if not v]
    print("  gates      " + ("all pass" if not bad else "FAIL: " + ", ".join(bad)))
    return not bad


def check(job: Job) -> bool:
    if not job.wav.exists():
        sys.exit(f"{job.wav} does not exist. Build it:  python3 tools/reel/audio.py {job.slug} {job.part}")
    narr = fit(decode(job.narration), job.n)
    m = measure(job, narr, read_wav16(job.wav))
    rep = json.loads(job.report.read_text(encoding="utf-8")) if job.report.exists() else {}
    ok = show(job, dict(rep, measured=m))
    if not rep:
        print(f"  no {job.report.name} beside it: per-cue numbers unavailable")
    elif rep["measured"] == m:
        print(f"  the file on disk is the one {job.report.name} describes (sha256 and every level match)")
    else:
        diff = [k for k in m if rep["measured"].get(k) != m[k]]
        print(f"  WARNING: the file on disk is NOT the one {job.report.name} describes; differs in: {', '.join(diff)}")
        ok = False
    if rep and job.cues_path.exists() and rep.get("cue_file") is None:
        print(f"  NOTE: {job.rel(job.cues_path)} exists now but this wav was built BED ONLY; rebuild")
    return ok


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("slug", help="work/<slug>")
    ap.add_argument("part", type=int, help="part number (1, 2, 3)")
    ap.add_argument("--check", action="store_true", help="measure the file on disk, change nothing")
    ap.add_argument("--cues", help="a cue file other than work/<slug>/out/cues_p<N>.json (testing)")
    ap.add_argument("--out", help="a folder other than work/<slug>/out/audio (testing)")
    a = ap.parse_args()
    job = Job(a.slug, a.part, a.cues, a.out)
    good = check(job) if a.check else show(job, build(job))
    sys.exit(0 if good else 1)
