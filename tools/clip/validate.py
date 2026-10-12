#!/usr/bin/env python3
"""Validate one part's spec against every hard rule before rendering.

    python3 tools/clip/validate.py <slug> --part 1
    python3 tools/clip/validate.py <slug> --spec spec/segments_part1.json

Zero errors chahiye. Warnings padho — aksar words/sec ka hota hai.

The spec is checked on paper here; tools/clip/qa.mjs then checks it on pixels.
"""
import json, re, glob, os, sys

CLIP = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(CLIP))


def _video(argv):
    if not argv or argv[0].startswith('--'):
        sys.exit("usage: validate.py <slug|folder> [--part N | --spec path]")
    ref = argv[0]
    d = os.path.abspath(ref) if '/' in ref else os.path.join(REPO, 'work', ref)
    if not os.path.isdir(d):
        sys.exit(f"no video folder: {d}")
    return d


def _opt(argv, k):
    for i, a in enumerate(argv):
        if a == f'--{k}' and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(f'--{k}='):
            return a.split('=', 1)[1]
    return None


ROOT = _video(sys.argv[1:])
_part, _spec = _opt(sys.argv, 'part'), _opt(sys.argv, 'spec')
# Parts never share a spec file: one part is validated without touching the
# spec another part is rendering from.
SPEC = os.path.join(ROOT, _spec) if _spec else \
       os.path.join(ROOT, 'spec', f'segments_part{_part}.json' if _part else 'segments.json')


def _css_px(name, fallback):
    """One `--name: 123px` out of the theme, so the gate reads the real layout.

    Copying the number here instead is how a gate goes quiet: this file carried
    `CAP_TOP = 1178` long after the band had moved. The engine's stylesheet is
    read first and the video's theme.css after it, so an override wins exactly
    as it does in the browser.
    """
    val = fallback
    for css_path in (os.path.join(CLIP, 'engine', 'style.css'), os.path.join(ROOT, 'theme.css')):
        try:
            with open(css_path, encoding='utf-8') as fh:
                css = fh.read()
        except OSError:
            continue
        m = re.search(r'^\s*%s\s*:\s*(\d+)px' % re.escape(name), css, re.M)
        if m:
            val = int(m.group(1))
    return val


if not os.path.exists(SPEC):
    sys.exit(f"not found: {SPEC}")

IDS = {}
# Recursive, and keyed by the path RELATIVE TO THE VIDEO FOLDER — which is how
# the spec refers to an asset. This globbed 'assets/*.svg' only and keyed by
# basename, so a diagram in PROCESS.md's own layout (assets/svg/) was reported
# MISSING and then every one of its ids as unknown: forty error lines for one
# wrong glob.
for f in glob.glob(os.path.join(ROOT, 'assets', '**', '*.svg'), recursive=True):
    src = open(f, encoding='utf-8').read()
    key = os.path.relpath(f, ROOT)
    IDS[key] = set(re.findall(r'id="([^"]+)"', src))
    # strip comments first: the rule is often quoted inside one
    bare = re.sub(r'<!--.*?-->', '', src, flags=re.S)
    if re.search(r'<text[\s>]', bare):
        print(f"  X {key}: has a real <text> element — labels must come from the spec")

# The hand-off this project subtracts from every caption's t_out. The stock
# rule below wants exactly 0.2s between phrases; this build uses 0.16 because
# the engine's pop_out was patched to fire AT t_out instead of 0.22s before it,
# so 0.16 is the whole of the early-clear rather than 0.16 on top of 0.22.
HANDOFF = 0.16

S = json.load(open(SPEC, encoding='utf-8'))
err, warn = [], []

for i, s in enumerate(S):
    sid = s.get("seg_id", f"#{i}")
    ph = s.get("phrases", [])
    # CAPTIONS ONLY ON AN EMPTY SCREEN.
    # A segment either puts something on the stage or shows captions - never
    # both. Stated as a gate rather than left as a convention, because it is
    # the kind of rule a later hand-edit silently breaks.
    # THIS THEME MOVED THE CAPTION BAND, so the rule above no longer applies to
    # it. The original assumed captions at y 100-340 against a stage at 380-850
    # - close enough that a caption over a diagram is genuinely crowded. This
    # video's approved design puts the band BELOW the stage and above the
    # presenter's floor: they share NO pixels. The check is kept and inverted
    # rather than deleted, so it still blocks the moment anyone moves the band
    # back without thinking.
    CAP_TOP = _css_px('--cap-top', 1178)
    STAGE_BOT = _css_px('--stage-top', 380) + _css_px('--stage-h', 470)
    on_stage = ("diagram" in s) or ("equation" in s)
    if on_stage and ph and CAP_TOP < STAGE_BOT:
        err.append(f"seg{sid}: has a {'diagram' if 'diagram' in s else 'equation'} "
                   f"AND {len(ph)} caption(s) - captions run only on an empty screen")
    if not ph:
        # A segment under the question card is not blank: the card IS the
        # picture there, and its captions are left out on purpose
        # (tools/build_spec.py, "CAPTIONS UNDER THE CARD ARE NOT DRAWN").
        if not on_stage and not s.get("under_card"):
            err.append(f"seg{sid}: no phrases and nothing on the stage - it is a blank segment")
        continue

    for p in ph:
        # Keep FULL precision for the comparisons below and round only for the
        # message. Rounding first turned 1.333 into 1.33 and failed it against a
        # 1.3333 floor — a build blocked by two decimal places.
        d_exact = p["t_out"] - p["t_in"]
        d = round(d_exact, 2)
        # THE FLOOR IS TEXT-AWARE HERE, AND ONLY HERE.
        # The stock rule is a flat 2.5s, and it is right for the normal
        # workflow: there the renderer owns the clock and HeyGen speaks the
        # line afterwards, so a caption can simply be given more time.
        # This project is the other way round - the clip already exists and the
        # SRT owns the clock. A clause the teacher says in 1.5s CANNOT be shown
        # for 2.5s without sitting on screen a second after he has moved on,
        # which is the desync this pass exists to remove. So the floor is what
        # the caption actually needs to be read: 4.5 words/sec, never under
        # 1.05s. It is still a real gate - it fails a ten-word caption held for
        # a second - it just cannot force the captions out of sync.
        floor = max(1.05, len(p["text"].split()) / 4.5)
        # 2ms of tolerance, because times are stored to 3dp and the floor is
        # not a round number: a caption padded to exactly the floor came back
        # as "1.33s < 1.33s" and failed the build by 0.3 of a millisecond.
        if d_exact < floor - 2e-3:
            err.append(f"seg{sid}: phrase {d}s < {floor:.2f}s needed to read "
                       f"{len(p['text'].split())} words  '{p['text'][:34]}'")
        if len(p["text"].split()) > 10:
            warn.append(f"seg{sid}: {len(p['text'].split())}-word phrase '{p['text'][:34]}'")
        g = p.get("golden")
        if g:
            if g not in p["text"]:
                err.append(f"seg{sid}: golden '{g}' not in its phrase")
            if "-" in g or "'" in g:
                err.append(f"seg{sid}: golden '{g}' has a hyphen/apostrophe (engine swaps hyphens)")
            if re.search(r"[+=()]|\u2212", p["text"]):
                err.append(f"seg{sid}: phrase has a math symbol, golden must be null")

    # CLIP-DRIVEN CLOCK. The three rules below were written for a spec that
    # OWNS the clock, where the author chooses every boundary. Here the audio
    # already exists and every time is measured off it, so:
    #   - the gap between captions is whatever pause the teacher takes: 0.0
    #     back-to-back, longer where he stops. Forcing a constant 0.16 is what
    #     cut 0.2s off every caption in an earlier build and read as the
    #     captions running ahead of the voice. An OVERLAP is still an error.
    #   - the first caption starts when he starts speaking, not at 0.0.
    #   - the last caption ends when his last word ends, not at the segment
    #     boundary; holding it to the boundary is the same desync.
    # This is the adaptation CLIP_VIDEO_RUNBOOK.md section 7 requires, and it
    # is deliberately narrow: each rule keeps a real failing condition.
    for a, b in zip(ph, ph[1:]):
        gap = round(b["t_in"] - a["t_out"], 2)
        if gap < 0:
            err.append(f"seg{sid}: captions overlap by {-gap}s")

    if ph[0]["t_in"] < 0:
        err.append(f"seg{sid}: first phrase starts before the segment")
    if round(ph[-1]["t_out"], 3) > round(s["duration"], 3) + 0.001:
        err.append(f"seg{sid}: last phrase ends {ph[-1]['t_out']}s, past the "
                   f"segment's {s['duration']}s - it would draw on a frame that does not exist")

    words = len(s["voiceover"].split())
    wps = words / s["duration"]
    if not (1.5 <= wps <= 2.7):
        warn.append(f"seg{sid}: {words} words = {wps:.2f} w/s (aim 1.8-2.4)")

    if "diagram" in s:
        a = s["diagram"]["asset"]
        valid = IDS.get(a)
        if valid is None:
            err.append(f"seg{sid}: MISSING ASSET {a}")
            valid = set()
        first_in, out_at = {}, {}
        for st in s["diagram"]["timeline"]:
            if st["id"] not in valid:
                err.append(f"seg{sid}: unknown id '{st['id']}' in {a}")
            if st["t"] + st.get("dur", 0) > s["duration"]:
                err.append(f"seg{sid}: step '{st['id']}' ends after {s['duration']}s")
            if st["action"] == "fade_in":
                first_in.setdefault(st["id"], st["t"])
            elif st["action"] == "fade_out":
                out_at.setdefault(st["id"], st["t"])
        # a shape that fades out less than a second after it faded in was never
        # really shown - see the label note above; segment 7's `why_pill` had
        # 0.27s of life and segment 4's `s_range` 0.72s.
        # NB: this loop used to bind `i`, which is the enclosing segment INDEX.
        # It shadowed it with a shape id (a string), and the next line —
        # `prev = S[i-1] if i > 0` — then compared str to int and crashed. Only
        # fires when a segment has both fades and carry_over, which is why it
        # sat here undetected.
        for shape_id, t_in in first_in.items():
            if shape_id in out_at and out_at[shape_id] - t_in < 1.0:
                err.append(f"seg{sid}: shape '{shape_id}' is on screen "
                           f"{out_at[shape_id] - t_in:.2f}s - it arrives and immediately leaves")
        prev = S[i-1] if i > 0 else None
        for c in s["diagram"]["carry_over"]:
            if c not in valid:
                err.append(f"seg{sid}: carry_over '{c}' not in {a}")
            if prev is not None:
                es = {e for e in prev.get("end_state", []) if not e.startswith("label:")}
                if c not in es:
                    err.append(f"seg{sid}: carry_over '{c}' not in seg{prev['seg_id']} end_state")

    for l in s.get("labels", []):
        if l["t_in"] > s["duration"] - 0.4:
            err.append(f"seg{sid}: label '{l['text']}' appears too late")
        # A LABEL MUST OUTLIVE ITS OWN ARRIVAL, AND BE READABLE ONCE IT HAS.
        # Both of these shipped past validate AND past qa.mjs on the first cut
        # of this part: anchoring a cue to a phrase that starts late in a long
        # segment, then clearing at the usual end-0.5, gave segment 7 a label
        # whose t_in (9.731) was AFTER its t_out (9.702). The engine popped it
        # in and never took it out, so it floated alone on a bare plate for the
        # last half second - the exact defect the runbook records. qa.mjs could
        # not see it: it samples for labels APPEARING, never for one that fails
        # to leave. Anything under a second is unreadable and is an error too.
        to = l.get("t_out")
        if to is not None:
            if l["t_in"] >= to:
                err.append(f"seg{sid}: label '{l['text']}' t_in {l['t_in']} is at or "
                           f"after its t_out {to} - it will never clear")
            elif to - l["t_in"] < 1.0:
                err.append(f"seg{sid}: label '{l['text']}' is on screen "
                           f"{to - l['t_in']:.2f}s - under 1s cannot be read")
        for k in ("x", "y"):
            if not (0.0 <= l[k] <= 1.0):
                err.append(f"seg{sid}: label '{l['text']}' {k}={l[k]} outside 0-1")

total = sum(x["duration"] for x in S)
withd = sum(1 for x in S if "diagram" in x)
capped = sum(x["duration"] for x in S if x.get("phrases"))
print(f"\n{len(S)} segments | {total:.0f}s | {withd} with diagrams")
print(f"captions on {capped:.1f}s ({capped/total:.0%}); "
      f"the other {total-capped:.1f}s carries a diagram or an equation")
print("\nERRORS:")
print("\n".join("  X " + e for e in err) if err else "  none")
print("\nWARNINGS:")
print("\n".join("  ! " + w for w in warn) if warn else "  none")
sys.exit(1 if err else 0)
