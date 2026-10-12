#!/usr/bin/env python3
"""Word timings for a HeyGen clip, via whisper.cpp.

PROMOTED OUT OF `work/bio-c2-la-01/` on 2026-09-09, unchanged.

PROCESS.md step 2 says "whisper.cpp, word timings", but the only tool in
`tools/` was `transcribe.py`, which loads openai-whisper `medium` — 1.5GB of
model on an 8GB machine, and the run that put 13GB into swap. This is the
whisper.cpp path that replaced it, and it lived inside ONE video's folder,
which is exactly the "still lives inside a work/<slug>/ folder and must be
copied" problem PROCESS.md names. BIO-C5-LA-01 then re-derived its timing by
hand because nothing in `tools/` did this.

`tools/transcribe.py` stays for the older projects/ track, whose words files
already came from it. New videos use this one.

    python3 transcribe.py <clip.wav> <captions.srt> <clip_seconds> <out.json>

Every flag here is load-bearing and each one cost a bad run to find.

  -nfa    DTW needs the cross-attention weights, and flash attention (ON by
          default) does not expose them.  With it enabled every token comes
          back `t_dtw: -1` and the timings are silently worthless.

  t_dtw   Read the timings off the TOKENS, not off `offsets`.  With `-ml 1` the
          segment offsets come back as nonsense (-1007.30 on an 18s cut) while
          t_dtw is correct, in centiseconds from the start of the cut.

  chunks  Whisper's window is 30s and long-form decoding drifts inside it: one
          segment swallowed 12.15->42.12 and returned a single short sentence
          for thirty seconds of speech.  Audio is cut on SRT cue boundaries
          into runs under 20s.  `-ot/-d` do NOT do this -- whisper still fills
          a 30s window and emits timestamps across all of it, which put words
          at 156.78s on a 133.40s clip.  The audio has to be physically cut.

  turbo   large-v3 is 3.1GB and this is an 8GB machine; it ran the laptop into
          swap for no measurable gain in transcription quality on this audio.

  -bs 1   Greedy.  Beam search 5 costs ~5x for nothing DTW can use.

And one that is not a flag: do not chunk per cue.  35 cues means 35 process
launches, each reloading the model and recompiling the Metal shader libraries
(~20s each).  That startup, not the decoding, was the entire wall time.
"""
import json, re, subprocess, sys, os, tempfile
from pathlib import Path

MODEL = os.environ.get(
    "WHISPER_MODEL", os.path.expanduser("~/.cache/whisper-cpp/ggml-large-v3-turbo.bin"))
DTW = os.environ.get("WHISPER_DTW", "large.v3.turbo")
MAX_CHUNK = 20.0
DENSE = 2.0              # words/sec below which a span is split and retried


def parse_srt(path):
    blocks, cur = [], []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip() == "":
            if cur:
                blocks.append(cur); cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append(cur)
    t = lambda h, m, s, ms: int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    out = []
    for b in blocks:
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", b[1])
        out.append({"i": int(b[0]), "s": t(*m.groups()[:4]), "e": t(*m.groups()[4:]),
                    "text": " ".join(b[2:])})
    return out


def chunks(cues, clip_end):
    """Runs of consecutive cues under MAX_CHUNK. Split only at a cue boundary,
    so a chunk edge never lands in the middle of a spoken line."""
    out, cur = [], None
    for c in cues:
        if cur is None:
            cur = {"s": c["s"], "e": c["e"], "cues": [c["i"]]}
        elif c["e"] - cur["s"] <= MAX_CHUNK:
            cur["e"] = c["e"]; cur["cues"].append(c["i"])
        else:
            out.append(cur); cur = {"s": c["s"], "e": c["e"], "cues": [c["i"]]}
    if cur:
        out.append(cur)
    out[0]["s"] = max(0.0, out[0]["s"] - 0.15)
    out[-1]["e"] = min(clip_end, out[-1]["e"] + 0.40)
    return out


def read_words(path, base, span):
    """`-ml 1` splits by TOKEN and a Devanagari character spans two or three of
    them, so a word's text is often a partial UTF-8 sequence and the file will
    not decode as UTF-8 at all.  latin-1 is lossless byte-wise and leaves the
    ASCII JSON structure intact, so the bytes survive to be rejoined here."""
    # strict=False: with -ml 1 a token's bytes can include a raw control character
    # (GEO-C2-LA-01 part 3, 2026-10-07), which the strict reader rejects outright.
    d = json.loads(path.read_text(encoding="latin-1"), strict=False)
    raw = []
    for seg in d["transcription"]:
        tk = [t for t in seg.get("tokens", []) if t.get("t_dtw", -1) >= 0]
        if not tk:
            continue
        raw.append({"b": seg["text"].encode("latin-1"),
                    "t": min(t["t_dtw"] for t in tk) / 100.0})
    words = []
    for i, r in enumerate(raw):
        text = r["b"].decode("utf-8", "replace").strip()
        if not text or "�" in text:
            continue
        end = raw[i + 1]["t"] if i + 1 < len(raw) else span
        words.append({"w": text,
                      "s": round(base + r["t"], 3),
                      "e": round(base + min(max(end, r["t"] + 0.06), span), 3)})
    return words


def decode(wav, start, end, tmpdir, cues, depth=0):
    """Decode a span, and subdivide it if it comes back sparse.

    A 20s chunk is fast but whisper still skips passages inside it -- cues 30-33
    came back at 0.9 words/sec against this speaker's 2.5.  Splitting every
    chunk to cue size would fix that and cost 35 model loads per part, so
    instead only the spans that actually fail get split, at a cue boundary, and
    the halves are re-decoded.  Most spans pass the first time."""
    words = run(wav, start, end, tmpdir)
    span = end - start
    inner = [c for c in cues if start < c["s"] < end - 1.0]
    if len(words) / max(span, 0.1) >= DENSE or span < 6.0 or not inner:
        return words, [(start, end, len(words), depth)]
    mid = min(inner, key=lambda c: abs(c["s"] - (start + end) / 2))["s"]
    a, la = decode(wav, start, mid, tmpdir, cues, depth + 1)
    b, lb = decode(wav, mid, end, tmpdir, cues, depth + 1)
    # keep the split only if it actually recovered speech
    if len(a) + len(b) > len(words):
        return a + b, la + lb
    return words, [(start, end, len(words), depth)]


def run(wav, start, end, tmpdir):
    piece, out = Path(tmpdir) / "piece.wav", Path(tmpdir) / "piece"
    subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}",
                    "-t", f"{end - start:.3f}", "-i", str(wav), "-ar", "16000",
                    "-ac", "1", "-c:a", "pcm_s16le", "-y", str(piece)], check=True)
    subprocess.run(["whisper-cli", "-m", MODEL, "-f", str(piece), "-l", "hi",
                    "-nfa", "-dtw", DTW, "-bs", "1", "-ml", "1", "-sow",
                    "-mc", "0", "-ojf", "-of", str(out), "-np", "-nt"],
                   check=True, capture_output=True)
    return read_words(Path(str(out) + ".json"), start, end - start)


def srt_gap(cues, a, b):
    """True if the silence between a and b is a pause the SRT also has."""
    return any(a - 0.8 <= c["e"] <= b + 0.8 and n["s"] - c["e"] > 0.5
               for c, n in zip(cues, cues[1:]))


# Mean level below which a window really is a pause. Speech in these clips sits
# around -18 dB mean; a genuine pause measures below -45. -40 leaves room for
# room tone and breath without excusing a window that has words in it.
QUIET_DB = -40.0


def is_quiet(wav, lo, hi):
    """Does the AUDIO agree that lo..hi is silence?

    `srt_gap` alone is not allowed to excuse a hole, because the SRT is the
    artefact this whole stage exists to distrust. BIO-C2-LA-01 is the case:
    whisper dropped `ये पूरी लाइन गाँठ बाँध लो, और` across part 2's 100.43-102.99
    and the delivered SRT happened to carry a cue break in the same place, so
    srt_gap called it a pause and fill_gaps skipped it. Measured, that window is
    -18.2 dB mean / -3.9 dB peak - speech, at conversational level, and
    silencedetect finds exactly ONE true pause in the whole of part 2 (at
    104.4s, which is not where any hole is). The line stranded in that gap then
    had to be interpolated, and shipped 1.20s off the voice.

    So the SRT may only CONFIRM a pause the audio already shows. If the audio is
    loud, the hole is dropped speech and gets re-decoded no matter what the SRT
    claims.
    """
    if hi - lo <= 0.05:
        return True
    try:
        p = subprocess.run(
            ["ffmpeg", "-nostdin", "-ss", f"{lo:.3f}", "-t", f"{hi - lo:.3f}",
             "-i", str(wav), "-af", "volumedetect", "-f", "null", "-"],
            capture_output=True, text=True, stdin=subprocess.DEVNULL)
        m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", p.stderr)
        # No reading is not evidence of silence - re-decode rather than skip.
        return float(m.group(1)) < QUIET_DB if m else False
    except Exception:                                     # noqa: BLE001
        return False


def fill_gaps(wav, words, cues, clip_end, tmpdir, rounds=6):
    """Re-decode any silence the AUDIO does not account for.

    A chunk seam can swallow a run of words and put a plausible-looking
    hallucination where they were: part 3 lost `परीक्षा में इसका आंसर कैसे
    लिखना है वो` across 126.08-128.42 and wrote `परिपकवन` over the join, which
    reads as fine until you check it against the audio.

    A hole is excused only when the SRT calls it a pause AND the audio measures
    like one - see `is_quiet` for the run that made the second half necessary.

    `rounds` is per-part and each round repairs ONE hole, so it has to exceed
    the number of holes in the worst part rather than the typical one. At 2,
    BIO-C2-LA-01 part 2 would repair its first hole and leave the second.
    """
    tried: set[tuple[float, float]] = set()
    for _ in range(rounds):
        hole = next(((a, b) for a, b in zip(words, words[1:])
                     if b["s"] - a["e"] > 1.2
                     and (a["e"], b["s"]) not in tried
                     and not (srt_gap(cues, a["e"], b["s"])
                              and is_quiet(wav, a["e"], b["s"]))), None)
        if hole is None:
            return words
        a, b = hole
        tried.add((a["e"], b["s"]))
        lo, hi = max(0.0, a["s"] - 0.6), min(b["e"] + 0.6, clip_end)
        patch = run(wav, lo, hi, tmpdir)
        if not patch:
            return words
        keep = [w for w in words if w["e"] <= lo + 0.05 or w["s"] >= hi - 0.05]
        print(f"     gap-fill {lo:.2f}-{hi:.2f}: "
              f"{len(words) - len(keep)} words -> {len(patch)}", flush=True)
        words = sorted(keep + patch, key=lambda x: (x["s"], x["e"]))
    return words


def split_long(wav, words, clip_end, tmpdir, rounds=8):
    """Re-decode any single token that swallowed seconds of speech.

    `fill_gaps` above repairs a SILENCE the SRT does not account for. This
    repairs the opposite shape, which the density check cannot see: no gap at
    all, because one token is holding the whole passage. BIO-C5-LA-01 part 2
    returned `'हैं।'` spanning 90.76-102.24 — ELEVEN AND A HALF SECONDS on one
    word — and that span is the six-step recap, the most important sentence in
    the part. The chunk around it decoded at 2.5 words/sec, comfortably over
    the density floor, so nothing upstream had any reason to look.

    A Hindi word cannot last more than about a second. Anything past LONG is
    re-decoded on its own span with a little margin; the result is kept only if
    it actually recovered more words, so a token that is genuinely just held
    survives rather than being replaced by a hallucination.

    `rounds` has to exceed the number of long tokens, not merely cover the worst
    one: at 3 it repaired the 11.5s swallow and then stopped with four smaller
    ones still unexamined, and the gate failed on those instead. It is also
    followed by another gap-fill in `main`, because a re-decode reaches a little
    past the token it replaces and can leave a silence at its own seam — this
    pass opened a 2.71s hole at 87.88 doing exactly that.
    """
    LONG = 1.30
    tried: set[tuple[float, float]] = set()
    for _ in range(rounds):
        bad = max((w for w in words
                   if w["e"] - w["s"] > LONG and (w["s"], w["e"]) not in tried),
                  key=lambda w: w["e"] - w["s"], default=None)
        if bad is None:
            return words
        tried.add((bad["s"], bad["e"]))
        lo, hi = max(0.0, bad["s"] - 0.25), min(bad["e"] + 0.25, clip_end)
        patch = run(wav, lo, hi, tmpdir)
        if len(patch) <= 1:
            print(f"     long {bad['s']:.2f}-{bad['e']:.2f} {bad['w']!r}: "
                  f"re-decode gave {len(patch)} word(s), left as is", flush=True)
            continue
        keep = [w for w in words if w["e"] <= lo + 0.05 or w["s"] >= hi - 0.05]
        print(f"     long-split {lo:.2f}-{hi:.2f}: "
              f"{len(words) - len(keep)} word(s) -> {len(patch)}", flush=True)
        words = sorted(keep + patch, key=lambda x: (x["s"], x["e"]))
    return words


def fill_ends(wav, words, clip_end, tmpdir):
    """Re-decode a HEAD or TAIL the transcript does not reach.

    `fill_gaps` only looks BETWEEN two words, so speech dropped before the
    first word or after the last is invisible to it and to the hole check.
    BIO-C4-LA-03 part 2 ended its transcript at 111.18s on a 115.68s clip, and
    the last 4.5s measured -20 dB mean: his closing sentence, gone, with the
    gate reading "holes>1.5s 0".
    """
    tail = clip_end - words[-1]["e"]
    if tail > 1.0 and not is_quiet(wav, words[-1]["e"], clip_end):
        lo = max(0.0, words[-1]["s"] - 3.0)
        patch = run(wav, lo, clip_end, tmpdir)
        keep = [w for w in words if w["e"] <= lo + 0.05]
        if patch and patch[-1]["e"] > words[-1]["e"] + 0.5:
            print(f"     tail-fill {lo:.2f}-{clip_end:.2f}: "
                  f"{len(words) - len(keep)} words -> {len(patch)}", flush=True)
            words = keep + patch
    head = words[0]["s"]
    if head > 1.0 and not is_quiet(wav, 0.0, head):
        hi = min(clip_end, words[0]["e"] + 3.0)
        patch = run(wav, 0.0, hi, tmpdir)
        keep = [w for w in words if w["s"] >= hi - 0.05]
        if patch and patch[0]["s"] < head - 0.5:
            print(f"     head-fill 0.00-{hi:.2f}: "
                  f"{len(words) - len(keep)} words -> {len(patch)}", flush=True)
            words = sorted(patch + keep, key=lambda x: (x["s"], x["e"]))
    return words


def main(wav, srt, clip_end, out_path):
    cues = parse_srt(srt)
    ch = chunks(cues, clip_end)
    print(f"{Path(wav).name}: {len(cues)} cues -> {len(ch)} chunks "
          f"({Path(MODEL).name})", flush=True)
    words = []
    with tempfile.TemporaryDirectory() as td:
        for n, c in enumerate(ch, 1):
            w, log = decode(wav, c["s"], c["e"], td, cues)
            print(f"  {n:2d}  cues {c['cues'][0]:>2}-{c['cues'][-1]:<2} "
                  f"{c['s']:7.2f}-{c['e']:7.2f}  {len(w):3d} words  "
                  f"{len(w) / max(c['e'] - c['s'], .1):4.1f}/s"
                  f"{'  split x%d' % len(log) if len(log) > 1 else ''}", flush=True)
            words += w
        words.sort(key=lambda x: (x["s"], x["e"]))
        words = fill_gaps(wav, words, cues, clip_end, td)
        words = split_long(wav, words, clip_end, td)
        words = fill_gaps(wav, words, cues, clip_end, td)
        words = fill_ends(wav, words, clip_end, td)
    dedup = []
    for w in words:
        if dedup and w["w"] == dedup[-1]["w"] and abs(w["s"] - dedup[-1]["s"]) < 0.30:
            dedup[-1]["e"] = max(dedup[-1]["e"], w["e"])
            continue
        dedup.append(w)
    words = dedup
    Path(out_path).write_text(json.dumps(words, ensure_ascii=False, indent=1),
                              encoding="utf-8")

    # the two checks the runbook makes mandatory, plus a monotonicity check
    holes = [(a["e"], b["s"]) for a, b in zip(words, words[1:]) if b["s"] - a["e"] > 1.5]
    long = [w for w in words if w["e"] - w["s"] > 1.3]
    back = [(a["s"], b["s"]) for a, b in zip(words, words[1:]) if b["s"] < a["s"]]
    print(f"  -> {out_path}")
    print(f"     {len(words)} words  span {words[0]['s']:.2f}-{words[-1]['e']:.2f} "
          f"(clip {clip_end})  {len(words) / clip_end:.1f}/s")
    print(f"     holes>1.5s {len(holes)}   over 1.3s {len(long)}   out of order {len(back)}"
          f"   uncovered tail {clip_end - words[-1]['e']:.2f}s")
    for a, b in holes:
        print(f"       hole  {a:7.2f} -> {b:7.2f}   {b - a:.2f}s")
    for w in long:
        print(f"       long  {w['s']:7.2f}-{w['e']:7.2f}  {w['e'] - w['s']:5.2f}s  {w['w']!r}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4])
