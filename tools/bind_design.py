#!/usr/bin/env python3
"""Bind a design written against the SCRIPT to the MEASURED clock.

    python3 tools/bind_design.py <slug> <part>

Reads   work/<slug>/spec/parts/design_part<N>.json   beats, authored before any timing exists
        work/<slug>/out/caption_edit_part<N>.json    which SRT cue each caption came from
        work/<slug>/out/lines_part<N>.json           the measured captions, with word ranges
        work/<slug>/out/words_part<N>.json           the measured words
Writes  work/<slug>/spec/parts/bound/design_part<N>.json   every `say` resolved to `wi`
        work/<slug>/spec/parts/bound/anchors_part<N>.json  beat -> [first line, last line]
        work/<slug>/spec/parts/bound/meta_part<N>.json     each line's cue; the card's last line

WHY THE DESIGN NO LONGER WAITS FOR THE CLOCK
--------------------------------------------
A design used to be written AFTER transcription and captioning, because it
named caption LINE indices (anchors) and transcript WORD indices (`wi`) — both
of which only exist once the clip has been measured. That put seven minutes of
design, and every SVG after it, behind the slowest machine step in the build.

But what a beat shows and when is a decision about the SCRIPT: "draw the
threshold level on देहली ऊर्जा" is the same instruction whatever second देहली
ऊर्जा turns out to be spoken at. So a beat names:

  "cues": [a, b]          the HeyGen SRT cues it covers (1-based, inclusive) —
                          the SRT exists the moment the drop lands
  "say": "देहली ऊर्जा"     on any step, label, list item or equation entry: land
                          on the onset of these spoken words (`dt` still applies)
  "out_say": "..."        a label's exit, the same way
  "say_n": 2              the 2nd occurrence inside the beat, when a word repeats

and this tool resolves them once the clock exists. A `say` that is not spoken
inside its beat's own lines stops the build, loudly: a silent fallback to the
beat start is exactly the half-second drift the word anchors exist to remove.

A beat with no "cues" keeps its hand-written anchors_part<N>.json entry and
its `wi` indices untouched, so designs made the old way still build.
"""
from __future__ import annotations

import difflib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.align import skel, spoken          # noqa: E402

MATCH = 0.75      # a spoken token and a transcript token are the same word at this ratio


def sk_tokens(text: str) -> list[str]:
    return [s for s in (skel(t) for t in spoken(text).split()) if s]


def srt_cues(path: Path) -> list[str]:
    blocks, cur = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(line)
    if cur:
        blocks.append(cur)
    return [" ".join(b[2:]) for b in blocks if len(b) >= 3]


def cue_of_lines(edit: list[dict], cues: list[str]) -> list[int]:
    """Each caption's SRT cue. The draft (tools/draft_captions.py) records it as
    `cue`; a hand-written edit may not, so fall back to text: walk the cues in
    order and give each caption the nearest-following cue its words match."""
    if all("cue" in e for e in edit):
        return [int(e["cue"]) for e in edit]
    out, at = [], 0
    for e in edit:
        mine = "".join(sk_tokens(e["text"]))
        best, best_r = at, -1.0
        for k in range(at, min(at + 3, len(cues))):
            r = difflib.SequenceMatcher(None, mine, "".join(sk_tokens(cues[k]))).ratio()
            if r > best_r:
                best, best_r = k, r
        out.append(best + 1)
        at = best
    return out


def find(phrase: str, words: list[dict], lo: int, hi: int, nth: int = 1) -> int | None:
    """Index of the first transcript word of `phrase`, searched in words[lo..hi]."""
    want = sk_tokens(phrase)
    if not want:
        return None
    ws = [skel(w["w"]) for w in words]
    # Same first consonant AND 0.75 similar. Similarity alone is loose on short
    # skeletons: 'इलेक्ट्रॉन' (lktrn) scored 0.75 against 'करण' (krn) on
    # CHE-C3-SA-07 and landed 16 words early. A miss here fails loudly; a false
    # match does not, so the guard leans toward the miss.
    r = lambda t, a: (difflib.SequenceMatcher(None, t, a).ratio()        # noqa: E731
                      if t and a and t[0] == a[0] else 0.0)
    seen, i = 0, lo
    while i <= hi:
        # a match never STARTS on a token with no skeleton ("2", "0.693"):
        # joined to the next word it reads as that word, one token early
        if not ws[i]:
            i += 1
            continue
        j, ok = i, True
        for t in want:
            if j > hi:
                ok = False
                break
            if r(t, ws[j]) >= MATCH:
                j += 1
                continue
            # Whisper sometimes breaks one word into two tokens (ऑक्सीकारक ->
            # AUXI + कारग). Only when BOTH halves are needed: if the next token
            # matches on its own, this is not the word, it is the one before it.
            # Both halves at least two consonants: 'के' + 'साथ' read as
            # 'कैथोड' on CHE-C3-SA-07 and put a heading six seconds early.
            if (j + 1 <= hi and len(ws[j]) >= 2 and len(ws[j + 1]) >= 2
                    and r(t, ws[j + 1]) < MATCH and r(t, ws[j] + ws[j + 1]) >= MATCH):
                j += 2
                continue
            ok = False
            break
        if ok:
            seen += 1
            if seen == nth:
                return i
            i = j            # count each occurrence once: resume after this one
        else:
            i += 1
    return None


# ---------------------------------------------------------------- equation ladders
# A derivation is shown as a LADDER: rows of an equation, built term by term as
# he reads them, the row being worked on boxed in gold, earlier rows dimmed,
# swapped-in terms gold, cancelled terms struck in red. The engine animates an
# equation as a base layer plus cross-faded highlight layers, and for nothing to
# shift as terms appear EVERY layer must be the whole block with the unshown
# terms transparent. Written by hand that is ~5KB of LaTeX per beat — CHE-C3-SA-06
# carried 34KB of it, and composing it was most of a 33-minute design. So a beat
# may give the ladder instead, and it is expanded here:
#
#   "ladder": {
#     "rows":  [["k", "=", {"frac": ["2.303", "t"]}, "\\log_{10}", {"frac": ["[A]_0", "[A]"]}],
#               ["t", "=", {"frac": ["2.303", "k"]}, "\\log_{10}", {"frac": ["[A]_0", "[A]"]}]],
#     "steps": [{"say": "k बराबर", "show": ["0.0", "0.1"]},
#               {"say": "बटे", "dt": -0.1, "show": ["0.2"]},
#               {"say": "मान", "show": ["1"], "gold": ["1.0", "1.2.1"]}] }
#
# Addresses: "r" a whole row, "r.i" term i of row r, "r.i.j" part j of a frac
# (0 numerator, 1 denominator), "r.i.j.k" piece k of a part given as a list —
# {"frac": ["[A]_0", ["[A]_0", "/2"]]} lets the [A]_0 below be struck while
# the /2 stays gold. A step may `show` (white), `gold`, `red`,
# `strike` (red, cancelled) or `white` (back to plain) any addresses; showing a
# term shows it in white unless it is also coloured in the same step.
GOLD, WHITE, DIM, RED = "#E8C25A", "#F2F2F2", "#8E97A8", "#FF5A5A"


def _leaves(rows):
    """Every addressable leaf: ("r.i") for a plain term, ("r.i.j") for a frac part."""
    out = []
    for r, row in enumerate(rows):
        for i, t in enumerate(row):
            if isinstance(t, dict) and "frac" in t:
                for j, part in enumerate(t["frac"]):
                    out += ([f"{r}.{i}.{j}.{k}" for k in range(len(part))] if isinstance(part, list)
                            else [f"{r}.{i}.{j}"])
            else:
                out.append(f"{r}.{i}")
    return out


def _expand(addrs, leaves):
    got = []
    for a in addrs:
        a = str(a)
        hit = [l for l in leaves if l == a or l.startswith(a + ".")]
        if not hit:
            raise ValueError(f"ladder address {a!r} names no term")
        got += hit
    return got


def _ladder_latex(rows, state, active):
    """state: leaf -> (colour or None for hidden, struck?)"""
    def leaf(addr, tex):
        colour, struck = state.get(addr, (None, False))
        body = f"\\cancel{{\\textcolor{{{colour}}}{{{tex}}}}}" if struck and colour else tex
        return f"\\textcolor{{{colour or 'transparent'}}}{{{body}}}"
    out = []
    for r, row in enumerate(rows):
        parts = []
        for i, t in enumerate(row):
            if isinstance(t, dict) and "frac" in t:
                sides = []
                for j, part in enumerate(t["frac"]):
                    sides.append("".join(leaf(f"{r}.{i}.{j}.{k}", x) for k, x in enumerate(part))
                                 if isinstance(part, list) else leaf(f"{r}.{i}.{j}", part))
                parts.append(f"\\dfrac{{{sides[0]}}}{{{sides[1]}}}")
            else:
                parts.append(leaf(f"{r}.{i}", t))
        box = GOLD if r == active else "transparent"
        out.append(f"&\\textcolor{{{box}}}{{\\boxed{{{''.join(parts)}}}}}")
    return "\\begin{aligned}" + "\\\\[10pt]".join(out) + "\\end{aligned}"


def expand_ladder(beat: dict):
    lad = beat.pop("ladder")
    rows, steps = lad["rows"], lad["steps"]
    leaves = _leaves(rows)
    state: dict[str, tuple] = {}
    layers, active = [], None
    for st in steps:
        for key, colour, struck in (("show", WHITE, False), ("white", WHITE, False),
                                    ("gold", GOLD, False), ("red", RED, False), ("strike", RED, True)):
            for a in _expand(st.get(key, []), leaves):
                if key == "show" and state.get(a, (None,))[0] not in (None, DIM):
                    continue                    # already shown and coloured: keep it
                state[a] = (colour, struck)
        shown_rows = [int(a.split(".")[0]) for a, (c, _) in state.items() if c]
        new_active = max(shown_rows) if shown_rows else None
        if new_active != active and active is not None:
            # a new row is being worked on: plain terms of the rows above go quiet
            for a, (c, k) in list(state.items()):
                if int(a.split(".")[0]) < new_active and c == WHITE:
                    state[a] = (DIM, k)
        active = new_active
        layer = {"latex": _ladder_latex(rows, state, active)}
        for k in ("say", "dt", "say_n", "wi", "t"):
            if k in st:
                layer[k] = st[k]
        layers.append(layer)
    eq = {"latex": _ladder_latex(rows, {}, None), "highlight": layers}
    for k in ("say", "dt", "say_n", "wi", "t_in"):
        if k in steps[0]:
            eq["say" if k == "say" else k] = steps[0][k]
    for k in ("t_out", "out_say"):
        if k in lad:
            eq[k] = lad[k]
    beat["equation"] = eq


def bind(beat: dict, lo: int, hi: int, words: list[dict], log: list[str], errors: list[str]):
    def walk(node, where):
        if isinstance(node, dict):
            for key, out in (("say", "wi"), ("out_say", "out_wi")):
                if key in node:
                    phrase = node.pop(key)
                    nth = int(node.pop("say_n", 1)) if key == "say" else 1
                    i = find(phrase, words, lo, hi, nth)
                    if i is None:
                        span = " ".join(w["w"] for w in words[lo:hi + 1])
                        errors.append(f"{beat['type']}: {where} says {phrase!r}"
                                      f"{f' (occurrence {nth})' if nth > 1 else ''}, which is not "
                                      f"spoken in its cues — words {lo}-{hi}: {span[:160]}")
                    else:
                        node[out] = i
                        log.append(f"  {beat['type']:<20} {where:<28} {phrase!r:<28} -> word {i} "
                                   f"{words[i]['w']!r} at {float(words[i]['s']):.2f}s")
            for k, v in node.items():
                walk(v, f"{where}.{k}" if where else k)
        elif isinstance(node, list):
            for n, v in enumerate(node):
                walk(v, f"{where}[{n}]")
    walk(beat, "")


def main() -> int:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    slug, part = sys.argv[1], int(sys.argv[2])
    root = Path("work") / slug
    design = json.loads((root / "spec" / "parts" / f"design_part{part}.json").read_text(encoding="utf-8"))
    edit = json.loads((root / "out" / f"caption_edit_part{part}.json").read_text(encoding="utf-8"))
    lines = json.loads((root / "out" / f"lines_part{part}.json").read_text(encoding="utf-8"))
    words = json.loads((root / "out" / f"words_part{part}.json").read_text(encoding="utf-8"))
    inputs = json.loads((root / "inputs.json").read_text(encoding="utf-8"))
    if len(edit) != len(lines):
        sys.exit(f"caption_edit has {len(edit)} entries but lines_part{part} has {len(lines)} — re-run retime")
    srt = next((p.get("captions") or {}).get("path") for p in inputs["parts"] if p["part"] == part)
    cues = srt_cues(Path(srt)) if srt else []
    cue_of = cue_of_lines(edit, cues)

    legacy_f = root / "spec" / "parts" / f"anchors_part{part}.json"
    legacy = json.loads(legacy_f.read_text(encoding="utf-8")) if legacy_f.is_file() else {}
    anchors, log, errors, owner = {}, [], [], {}
    for beat in design:
        name = beat["type"]
        if "cues" in beat:
            a, b = beat["cues"]
            mine = [i for i, c in enumerate(cue_of) if a <= c <= b]
            if not mine:
                errors.append(f"{name}: cues {a}-{b} match no caption line")
                continue
            first, last = mine[0], mine[-1]
            if mine != list(range(first, last + 1)):
                errors.append(f"{name}: cues {a}-{b} are not contiguous in the captions")
                continue
        elif name in legacy:
            first, last = legacy[name]
        else:
            continue            # a beat nothing anchors: merge_design keeps it, build_spec ignores it
        for k in range(first, last + 1):
            if k in owner:
                errors.append(f"line {k} claimed by both {owner[k]} and {name}")
            owner[k] = name
        anchors[name] = [first, last]
        if "ladder" in beat:
            try:
                expand_ladder(beat)
            except (ValueError, KeyError, IndexError) as e:
                errors.append(f"{name}: ladder — {e}")
                continue
        lo, hi = lines[first]["w"][0], lines[last]["w"][1]
        bind(beat, lo, hi, words, log, errors)
        # An equation's layers cross-fade in ORDER. A short formula token
        # ("4H", "से") skeletons to one letter and can match an earlier word —
        # on CHE-C3-SA-07 "4H" landed on "है", before the PbO₂ step it follows,
        # and the frames would have played out of order without an error.
        eq = beat.get("equation") or {}
        seq = [eq.get("wi")] + [h.get("wi") for h in eq.get("highlight", [])]
        seq = [(n, i) for n, i in enumerate(seq) if i is not None]
        for (na, a), (nb, b) in zip(seq, seq[1:]):
            if b < a:
                errors.append(f"{name}: equation layer {nb} lands on word {b} "
                              f"({words[b]['w']!r}), BEFORE layer {na} on word {a} — "
                              f"anchor it on a word after, or use say_n")
        beat.pop("cues", None)

    card = json.loads((root / "video.json").read_text(encoding="utf-8")).get("card") or {}
    card_last = None
    if card.get("part") == part and card.get("last_cue"):
        under = [i for i, c in enumerate(cue_of) if c <= int(card["last_cue"])]
        card_last = under[-1] if under else None

    if errors:
        print(f"[FAIL] {slug} part {part} — {len(errors)} problem(s) binding the design:")
        for e in errors:
            print("   ", e)
        return 1
    out = root / "spec" / "parts" / "bound"
    out.mkdir(parents=True, exist_ok=True)
    for name, obj in ((f"design_part{part}.json", design), (f"anchors_part{part}.json", anchors),
                      (f"meta_part{part}.json", {"cue_of_line": cue_of, "card_last_line": card_last})):
        tmp = out / f".{name}.tmp{os.getpid()}"
        tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, out / name)
    print(f"[ok] {slug} part {part} — {len(anchors)} beat(s) on {len(owner)} of {len(lines)} caption "
          f"line(s); {len(log)} spoken anchor(s) resolved" +
          (f"; card covers lines 0-{card_last}" if card_last is not None else ""))
    print("\n".join(log))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
