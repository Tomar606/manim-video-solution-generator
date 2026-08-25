#!/usr/bin/env python3
"""Validate spec/segments.json against every hard rule before rendering.

    cd <renderer folder> && python3 validate.py

Zero errors chahiye. Warnings padho — aksar words/sec ka hota hai.
"""
import json, re, glob, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(ROOT, 'spec', 'segments.json')
if not os.path.exists(SPEC):
    sys.exit(f"not found: {SPEC}\nrun this from inside the renderer folder")

IDS = {}
for f in glob.glob(os.path.join(ROOT, 'assets', '*.svg')):
    src = open(f, encoding='utf-8').read()
    key = 'assets/' + os.path.basename(f)
    IDS[key] = set(re.findall(r'id="([^"]+)"', src))
    # strip comments first: the rule is often quoted inside one
    bare = re.sub(r'<!--.*?-->', '', src, flags=re.S)
    if re.search(r'<text[\s>]', bare):
        print(f"  X {key}: has a real <text> element — labels must come from the spec")

S = json.load(open(SPEC, encoding='utf-8'))
err, warn = [], []

for i, s in enumerate(S):
    sid = s.get("seg_id", f"#{i}")
    ph = s.get("phrases", [])
    if not ph:
        err.append(f"seg{sid}: no phrases"); continue

    for p in ph:
        d = round(p["t_out"] - p["t_in"], 2)
        if d < 2.5:
            err.append(f"seg{sid}: phrase {d}s < 2.5s  '{p['text'][:34]}'")
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

    for a, b in zip(ph, ph[1:]):
        gap = round(b["t_in"] - a["t_out"], 2)
        if abs(gap - 0.2) > 0.001:
            err.append(f"seg{sid}: gap {gap}s between phrases (need exactly 0.2)")

    if ph[0]["t_in"] != 0.0:
        err.append(f"seg{sid}: first phrase must start at 0.0")
    if ph[-1]["t_out"] != s["duration"]:
        err.append(f"seg{sid}: last phrase must end at {s['duration']}")

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
        for st in s["diagram"]["timeline"]:
            if st["id"] not in valid:
                err.append(f"seg{sid}: unknown id '{st['id']}' in {a}")
            if st["t"] + st.get("dur", 0) > s["duration"]:
                err.append(f"seg{sid}: step '{st['id']}' ends after {s['duration']}s")
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
        for k in ("x", "y"):
            if not (0.0 <= l[k] <= 1.0):
                err.append(f"seg{sid}: label '{l['text']}' {k}={l[k]} outside 0-1")

total = sum(x["duration"] for x in S)
withd = sum(1 for x in S if "diagram" in x)
print(f"\n{len(S)} segments | {total:.0f}s | {withd} with diagrams")
print("\nERRORS:")
print("\n".join("  X " + e for e in err) if err else "  none")
print("\nWARNINGS:")
print("\n".join("  ! " + w for w in warn) if warn else "  none")
sys.exit(1 if err else 0)
